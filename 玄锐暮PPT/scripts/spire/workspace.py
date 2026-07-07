import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectPaths:
    root: Path
    output: Path
    temp: Path
    images: Path
    assets: Path
    qa: Path


def find_workspace_root(start_dir=None):
    """从指定目录向上查找工作区根目录。

    检测标记文件：CLAUDE.md、.git、.claude
    如果找不到，返回当前工作目录。
    """
    current = Path(start_dir or os.getcwd()).resolve()
    markers = ["CLAUDE.md", ".git", ".claude"]

    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    # 检查根目录本身
    for marker in markers:
        if (current / marker).exists():
            return current

    # 找不到标记文件，回退到当前工作目录
    return Path(os.getcwd()).resolve()


def create_project_workspace(project_name, base_dir=None):
    """创建PPT项目工作目录。

    除非用户明确指定 base_dir，否则自动使用工作区根目录。
    目录结构：{工作区根目录}/玄锐暮PPT/{项目名}/

    Args:
        project_name: 项目名称（如"毕业设计"）
        base_dir: 可选，用户明确指定的基础目录。未指定时自动检测工作区根目录。
    """
    paths = get_project_paths(project_name, base_dir=base_dir)
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.output.mkdir(exist_ok=True)
    paths.temp.mkdir(exist_ok=True)
    paths.images.mkdir(exist_ok=True)
    paths.assets.mkdir(exist_ok=True)
    paths.qa.mkdir(exist_ok=True)
    return paths


def get_project_paths(project_name, base_dir=None):
    """获取PPT项目路径。

    除非用户明确指定 base_dir，否则自动使用工作区根目录。
    路径结构：{工作区根目录}/玄锐暮PPT/{项目名}/

    Args:
        project_name: 项目名称（如"毕业设计"）
        base_dir: 可选，用户明确指定的基础目录。未指定时自动检测工作区根目录。
    """
    if base_dir is None:
        base_dir = find_workspace_root()
    root = Path(base_dir) / "玄锐暮PPT" / project_name
    return ProjectPaths(
        root=root,
        output=root / "生成",
        temp=root / "临时",
        images=root / "图片素材",
        assets=root / "其他素材",
        qa=root / "质检",
    )


def list_projects(base_dir=None):
    if base_dir is None:
        base_dir = find_workspace_root()
    workspace = Path(base_dir) / "玄锐暮PPT"
    if not workspace.exists():
        return []
    return [d.name for d in workspace.iterdir() if d.is_dir()]


def get_image_assets(project_name, base_dir=None):
    paths = get_project_paths(project_name, base_dir=base_dir)
    if not paths.images.exists():
        return []
    return [str(f) for f in paths.images.iterdir() if f.is_file()]


def cleanup_project(project_name, base_dir=None, keep_checkpoints=False):
    """清理项目临时文件和质检产物，只保留最终PPT。

    Args:
        project_name: 项目名称
        base_dir: 可选，基础目录
        keep_checkpoints: 是否保留检查点文件（默认删除）

    清理范围：
    - 临时/ 目录下的所有文件
    - 质检/ 目录下的所有截图和报告
    - 检查点目录（除非 keep_checkpoints=True）
    保留：
    - 生成/ 目录下的最终PPT文件
    - 图片素材/ 目录（用户可能手动添加了图片）
    """
    import shutil

    paths = get_project_paths(project_name, base_dir=base_dir)

    cleaned = []

    # 清理临时目录
    if paths.temp.exists():
        for f in paths.temp.iterdir():
            if f.is_file():
                f.unlink()
                cleaned.append(str(f))
            elif f.is_dir():
                shutil.rmtree(f)
                cleaned.append(str(f))

    # 清理质检目录
    if paths.qa.exists():
        for f in paths.qa.iterdir():
            if f.is_file():
                f.unlink()
                cleaned.append(str(f))

    # 清理检查点目录
    if not keep_checkpoints:
        checkpoint_dir = paths.root / "pptx-checkpoints"
        if checkpoint_dir.exists():
            shutil.rmtree(checkpoint_dir)
            cleaned.append(str(checkpoint_dir))

    return cleaned
