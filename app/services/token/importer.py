"""Token 文件自动导入（启动时执行，非侵入式）"""

import orjson
from pathlib import Path
from typing import Optional

from app.core.logger import logger
from app.core.storage import DATA_DIR


# 默认导入文件路径（data 目录）
DEFAULT_IMPORT_FILE = DATA_DIR / "sso_tokens.json"

DEFAULT_POOL = "ssoBasic"


async def import_tokens_from_file(file_path: Optional[Path] = None):
    """
    从 JSON 文件导入 Token 到池中。

    通过 TokenManager.add() 公开接口导入，已存在的 token 自动跳过。
    文件保留不删除，通过去重避免重复导入。

    JSON 格式：
        {"sso_tokens": ["token1", "token2", ...]}

    所有 token 导入到 ssoBasic 池。
    """
    path = file_path or DEFAULT_IMPORT_FILE
    if not path.exists():
        return

    from app.services.token.manager import get_token_manager

    try:
        with open(path, "rb") as f:
            data = orjson.loads(f.read())
    except Exception as e:
        logger.warning(f"Import: failed to parse {path.name}: {e}")
        return

    tokens = data.get("sso_tokens")
    if not isinstance(tokens, list) or not tokens:
        logger.debug(f"Import: {path.name} has no sso_tokens, skipped")
        return

    mgr = await get_token_manager()
    imported = 0
    skipped = 0
    errors = 0

    for idx, token_str in enumerate(tokens):
        if not isinstance(token_str, str) or not token_str.strip():
            logger.warning(f"Import: index {idx} invalid token, skipped")
            errors += 1
            continue

        added = await mgr.add(token_str.strip(), DEFAULT_POOL)
        if added:
            imported += 1
        else:
            skipped += 1

    if imported or skipped or errors:
        logger.info(
            f"Import: file={path.name}, imported={imported}, "
            f"skipped(duplicate)={skipped}, errors={errors}"
        )
