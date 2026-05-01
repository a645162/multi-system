"""
Prompt 主题模板管理
"""

from dataclasses import dataclass

from multi_system.system.shells.shell_base import RCFileManager


@dataclass
class PromptTheme:
    name: str
    description: str
    bash_ps1: str
    zsh_prompt: str


THEMES: list[PromptTheme] = [
    PromptTheme(
        name="classic",
        description="经典样式: user@host:dir$",
        bash_ps1=r"\u@\h:\w\$ ",
        zsh_prompt="%n@%m:%~%# ",
    ),
    PromptTheme(
        name="minimal",
        description="极简样式: dir$",
        bash_ps1=r"\W\$ ",
        zsh_prompt="%1~%# ",
    ),
    PromptTheme(
        name="full-path",
        description="完整路径: /full/path$",
        bash_ps1=r"\$PWD\$ ",
        zsh_prompt="%/$# ",
    ),
    PromptTheme(
        name="git-info",
        description="Git分支: dir (branch)$",
        bash_ps1=r'\W$(__git_ps1 " (%s)")\$ ',
        zsh_prompt='%1~$(git_prompt_info)%# ',
    ),
    PromptTheme(
        name="timestamp",
        description="带时间戳: [HH:MM] user@dir$",
        bash_ps1=r"[\t] \u@\W\$ ",
        zsh_prompt="[%*] %n@%1~%# ",
    ),
]

_PS1_RE_BASH = r"^PS1=.*$"
_PS1_RE_ZSH = r"^PROMPT=.*$"


class PromptThemeManager:
    def __init__(self, shell: str):
        self._rc = RCFileManager(shell)
        self.shell = shell

    def list_themes(self) -> list[PromptTheme]:
        return THEMES

    def get_theme(self, name: str) -> PromptTheme | None:
        return next((t for t in THEMES if t.name == name), None)

    def apply_theme(self, theme: PromptTheme) -> None:
        content = self._rc.read_rc()
        lines = content.splitlines(keepends=True)
        pattern = _PS1_RE_BASH if self.shell == "bash" else _PS1_RE_ZSH

        import re
        new_lines = []
        replaced = False
        for line in lines:
            if re.match(pattern, line.strip()):
                new_lines.append(f"# {line}" if not line.strip().startswith("#") else line)
                replaced = True
            else:
                new_lines.append(line)

        ps1_line = f'PS1="{theme.bash_ps1}"\n' if self.shell == "bash" else f'PROMPT="{theme.zsh_prompt}"\n'
        new_lines.append(ps1_line)
        self._rc.write_rc("".join(new_lines))

    def apply_custom(self, ps1_value: str) -> None:
        content = self._rc.read_rc()
        lines = content.splitlines(keepends=True)
        import re
        pattern = _PS1_RE_BASH if self.shell == "bash" else _PS1_RE_ZSH
        new_lines = []
        for line in lines:
            if re.match(pattern, line.strip()):
                new_lines.append(f"# {line}" if not line.strip().startswith("#") else line)
            else:
                new_lines.append(line)
        key = "PS1" if self.shell == "bash" else "PROMPT"
        new_lines.append(f'{key}="{ps1_value}"\n')
        self._rc.write_rc("".join(new_lines))
