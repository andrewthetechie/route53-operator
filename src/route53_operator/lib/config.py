import os
from functools import lru_cache
from typing import Any

from aiobotocore.config import AioConfig
from pydantic import AnyUrl
from pydantic import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """Configuration for the operator."""

    # AWS variables
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html
    aws_access_key_id: str | None = Field(None, description="AWS Access Key ID")
    aws_secret_access_key: str | None = Field(None, description="AWS Secret Access Key")
    aws_session_token: str | None = Field(None, description="AWS Session Token")
    aws_user_agent: str | None = Field(
        "route53-operator", description="User agent for AWS requests"
    )
    aws_user_agent_append: str | None = Field(
        None, description="A string to append to the default default user agent"
    )
    aws_connection_timeout: int | None = Field(
        60, description="Timeout for AWS requests"
    )
    aws_proxies: dict[str, AnyUrl] | None = Field(
        None,
        description="Proxies to use for AWS requests. e.g.: {'http': 'foo.bar:3128', 'http://hostname': 'foo.bar:4012'}",
    )
    aws_proxy_ca_bundle: str | None = Field(
        None, description="Path to a CA bundle to use for AWS requests"
    )
    aws_proxy_client_cert: str | None = Field(
        None, description="Path to a client certificate to use for AWS requests"
    )
    aws_proxy_use_forwarding_for_https: bool | None = Field(
        None, description="Whether to use the X-Forwarded-For header for HTTPS requests"
    )
    aws_client_cert: str | None = Field(
        None, description="Path to a client certificate to use for AWS requests"
    )
    aws_use_ssl: bool = Field(True, description="Whether to use SSL for AWS requests")
    aws_verify_ssl: bool = Field(
        True, description="Whether to verify SSL certificates for AWS requests"
    )
    aws_endpoint_url: AnyUrl | None | None = Field(
        None, description="The complete URL to use for the constructed client."
    )

    class Config:
        """Pydantic base setting config"""

        env_prefix = os.environ.get("CONFIG_PREFIX", "")

    @property
    def aws_session_kwargs(self) -> dict[str, Any]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html
        to_return = {}
        session_vars = [
            "aws_access_key_id",
            "aws_secret_access_key",
            "aws_session_token",
        ]
        for var in session_vars:
            if getattr(self, var) is not None:
                to_return[var] = getattr(self, var)
        return to_return

    @property
    def aws_client_kwargs(self) -> dict[str, str | bool | AnyUrl | AioConfig]:
        # https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html
        def build_config(config: "Config") -> AioConfig:
            config_kwargs = {}
            config_vars = [
                "aws_user_agent",
                "aws_user_agent_append",
                "aws_connection_timeout",
                "aws_proxies",
            ]
            for var in config_vars:
                if getattr(config, var) is not None:
                    config_kwargs[var.lstrip("aws_")] = getattr(config, var)
            proxies_config = {}
            proxies_vars = [
                "aws_proxy_ca_bundle",
                "aws_proxy_client_cert",
                "aws_proxy_use_forwarding_for_https",
            ]
            for var in proxies_vars:
                if getattr(self, var) is not None:
                    proxies_config[var.lstrip("aws_")] = getattr(self, var)
            if len(proxies_config.keys()) > 0:
                config_kwargs["proxies"] = proxies_config
            return AioConfig(**config_kwargs)

        to_return = {}
        to_return.update(self.aws_session_kwargs)
        if self.aws_verify_ssl is not None:
            to_return["verify"] = self.aws_verify_ssl
        for value in ["aws_use_ssl", "aws_endpoint_url"]:
            if getattr(self, value) is not None:
                to_return[value.lstrip("aws_")] = getattr(self, value)
        to_return["config"] = build_config(self)
        return to_return

    def __hash__(self):
        return hash(self.json())


@lru_cache
def get_config() -> Config:
    """Gets a config object from the env and returns it
    LRU cached so subsequent calls don't have to do the env lookups

    Returns:
        Config -- config object
    """
    return Config()
