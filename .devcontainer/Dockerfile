FROM mcr.microsoft.com/vscode/devcontainers/python:3.8

RUN git clone https://github.com/pyenv/pyenv.git /home/vscode/.pyenv && echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /home/vscode/.bash_profile \
	&& echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /home/vscode/.bash_profile && echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> /home/vscode/.bash_profile
	
RUN apt-get update && apt-get install git

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
	&& unzip awscliv2.zip && ./aws/install