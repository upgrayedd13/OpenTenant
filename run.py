#!/usr/bin/env -S uv run

from pathlib import Path
import subprocess
import argparse
import secrets
import sys
import os
import re


ENVIRONMENTS = ['production', 'development']
DEFAULT_KEY='dev-fallback-key'


def setup_env(env_file: str, env_str: str) -> dict[str, str]:
    root_dir = Path(__file__).parent
    if env_str == 'production':
        compose_files = [root_dir / 'docker-compose.yml']
    else:
        compose_files = [root_dir / 'docker-compose.yml', root_dir / 'docker-compose.override.yml']

    env = os.environ.copy()
    env['COMPOSE_FILE'] = os.pathsep.join(map(str, compose_files))
    env['COMPOSE_ENV_FILE'] = env_file
    return env


def docker_run(args: list[str], env_file: str, env_str: str, verbose: bool=False) -> None:
    cmd = ['docker', 'compose']
    if env_str == 'production':
        cmd += ['--profile', env_str] 
    cmd += ['--env-file', env_file, *args]

    if verbose:
        print(' '.join(cmd))

    try:
        subprocess.run(cmd, check=True, env=setup_env(env_file, env_str))
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError:
        sys.exit(4)


def docker_up(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    cmd = ['up', '--build']
    if args.environment == 'production':
        cmd.append('-d')
    cmd += args.SERVICE
    docker_run(cmd, env_file, args.environment, verbose)


def docker_down(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    cmd = ['down', *args.SERVICE]
    docker_run(cmd, env_file, args.environment, verbose)


def docker_restart(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    docker_down(args, env_file, verbose)
    docker_up(args, env_file, verbose)


def docker_logs(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    cmd = ['logs', '-f', *args.SERVICE]
    docker_run(cmd, env_file, args.environment, verbose)


def docker_config(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    cmd = ['config', *args.SERVICE]
    docker_run(cmd, env_file, args.environment, verbose)


def docker_ps(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    cmd = ['ps', *args.SERVICE]
    docker_run(cmd, env_file, args.environment, verbose)


def docker_shell(args: argparse.Namespace, env_file: str, verbose: bool=False) -> None:
    cmd = ['exec', '-it', '-u', 'root', args.SERVICE, args.SHELL_APP]
    docker_run(cmd, env_file, args.environment, verbose)


def determine_environment(env_arg: str, verbose: bool=False) -> str:
    root_dir = Path(__file__).parent

    if env_arg:
        return str((root_dir / f'.env.{env_arg}').resolve())

    possible_env_files = [root_dir / f'.env.{env}' for env in ENVIRONMENTS]
    existing = [env_file for env_file in possible_env_files if env_file.is_file()]
    if verbose:
        print(f'Found env files: {' '.join(fname for fname in existing)}')

    if len(existing) == 1:
        env_file = str(existing[0].resolve())
        if verbose:
            print(f'Using env file "{env_file}"')
        return env_file

    if len(existing) == 0:
        print('No expected environment files exist! Please rerun and specify an environment!', file=sys.stderr)
        sys.exit(1)

    print('Multiple expected environment files exist! Please rerun and specify an environment!', file=sys.stderr)
    sys.exit(2)


def create_environment_file(env_file: str, env: str) -> None:
    root_dir = Path(__file__).parent
    example_file = root_dir / '.env.example'
    if not example_file.is_file():
        print(f'Failed to find {example_file}!', file=sys.stderr)
        sys.exit(3)

    data = example_file.read_text()

    if env == 'development':
        log_level = 'DEBUG'
        db = 'opentenant_dev'
        db_password = DEFAULT_KEY
        secret_key = DEFAULT_KEY
    else:
        log_level = 'INFO'
        db = 'opentenant'
        db_password = secrets.token_urlsafe(64)
        secret_key = secrets.token_urlsafe(64)

    data = re.sub(r'ENV=.*', f'ENV={env}', data)
    data = re.sub(r'LOG_LEVEL=.*', f'LOG_LEVEL={log_level}', data)
    data = re.sub(r'POSTGRES_DB=.*', f'POSTGRES_DB={db}', data)
    data = re.sub(r'POSTGRES_PASSWORD=.*', f'POSTGRES_PASSWORD={db_password}', data)
    data = re.sub(r'SECRET_KEY=.*', f'SECRET_KEY={secret_key}', data)

    env_path = Path(env_file)
    print(f'Creating {env_path} from {example_file}...')
    env_path.write_text(data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Wrapper for docker compose commands for this application.')
    parser.add_argument('-e', '--environment', type=str, choices=ENVIRONMENTS, default='', help='Environment file to use. If not specified, the app will attempt to automatically determine which to use.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Causes the script to print more verbose output.')
    commands = parser.add_subparsers(dest='command', required=True)

    up_parser = commands.add_parser('up', help='Bring services up.')
    up_parser.add_argument('SERVICE', nargs='*', help='Services to bring up. If none specified, all will be brought up.')
    up_parser.set_defaults(func=docker_up)

    down_parser = commands.add_parser('down', help='Take services down.')
    down_parser.add_argument('SERVICE', nargs='*', help='Services to bring up. If none specified, all will be taken down.')
    down_parser.set_defaults(func=docker_down)

    restart_parser = commands.add_parser('restart', help='Restart services.')
    restart_parser.add_argument('SERVICE', nargs='*', help='Services to bring up. If none specified, all will be restarted.')
    restart_parser.set_defaults(func=docker_restart)

    logs_parser = commands.add_parser('logs', help='Display service logs')
    logs_parser.add_argument('SERVICE', nargs='*', help='Services to display args from. If none specified, all will be displayed.')
    logs_parser.set_defaults(func=docker_logs)

    config_parser = commands.add_parser('config', help='Print configs for services.')
    config_parser.add_argument('SERVICE', nargs='*', help='Services to display configs from. If none specified, all will be displayed.')
    config_parser.set_defaults(func=docker_config)

    ps_parser = commands.add_parser('ps', help='Print status of running services.')
    ps_parser.add_argument('SERVICE', nargs='*', help='Services to display info from. If none specified, all will be displayed.')
    ps_parser.set_defaults(func=docker_ps)

    shell_parser = commands.add_parser('shell', help='Access shell for service.')
    shell_parser.add_argument('SERVICE', help='Service name to connect to.')
    shell_parser.add_argument('SHELL_APP', default='/bin/sh', nargs='?', help='Interactive shell application to use.')
    shell_parser.set_defaults(func=docker_shell)

    return parser.parse_args()


def main() -> None:
    # parse command line arguments
    args = parse_args()

    # determine the environment to use
    env_file = determine_environment(args.environment)

    # set the environment based on the environment file
    args.environment = os.path.basename(env_file).split('.')[-1]

    # if the environment doesn't exist, create it
    if not os.path.isfile(env_file):
        if args.verbose:
            print('Creating environment file')
        create_environment_file(env_file, args.environment)

    # run the function
    args.func(args, env_file, args.verbose)


if __name__ == '__main__':
    main()
