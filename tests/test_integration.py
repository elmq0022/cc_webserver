import pathlib

import pytest
import requests


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        return False
    except Exception:
        return False


@pytest.fixture(scope="session")
def docker_compose_file():
    return pathlib.Path(__file__).parent.parent.absolute() / "docker-compose.yml"


@pytest.fixture(scope="session")
def http_server(docker_ip, docker_services):
    """Ensure that HTTP service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("http-server", 8888)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=0.1,
        check=lambda: is_responsive(url)
    )
    return url


@pytest.mark.parametrize(
    "server_path,expected_status_code",
    [
        pytest.param("/", 200, id="root"),
        pytest.param("/index.html", 200, id="root"),
        pytest.param("/abc", 400, id="directory does not exist"),
        pytest.param("/file-does-not-exist.html", 400, id="file does not exist"),
    ]
)
def test_http_server__returns_index_html(server_path, expected_status_code, http_server):
    resp = requests.get(f"{http_server}{server_path}")
    assert resp.status_code == expected_status_code
