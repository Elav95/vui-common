import platform


async def identify_architecture_service():
    architecture = platform.machine()

    identify = False
    if architecture == 'AMD64' or architecture == 'x86_64':
        identify = True
        arch = 'amd64'
    elif architecture.startswith('arm'):
        identify = True
        arch = 'arm'
    elif architecture.startswith('aarch64'):
        identify = True
        arch = 'arm64'
    else:
        arch = 'Error: Unsupported architecture'

    output = {'arch': arch, }
    if not identify:
        output['platform'] = platform.machine()

    return output
