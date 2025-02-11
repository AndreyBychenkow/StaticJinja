import argparse
import os
import shutil
import sys
from pathlib import Path
from staticjinja import Site


def get_context() -> dict:
    context = {
        "github_url": os.getenv("SJP_GITHUB_URL",
                                "https://github.com/AndreyBychenkow"),
        "github_title": os.getenv("SJP_GITHUB_TITLE", "Мой GitHub"),
        "title": os.getenv("SJP_TITLE", "Мой сайт")
    }
    return context


def main() -> None:
    parser = argparse.ArgumentParser(description="Генератор статических сайтов")
    parser.add_argument("-w", "--watch", action="store_true",
                        help="Режим отслеживания изменений")
    parser.add_argument("--srcpath", default=Path("MyTemplates"), type=Path)
    parser.add_argument("--outpath", default=Path("MyAssembly"), type=Path)

    args = parser.parse_args()

    if not args.srcpath.exists():
        print(f"Ошибка: Каталог с исходниками '{args.srcpath}' не найден.",
              file=sys.stderr)
        sys.exit(1)

    try:
        _ = list(args.srcpath.iterdir())
    except PermissionError:
        print(f"Ошибка: Недостаточно прав доступа и листинга файлов в каталоге "
              f"'{args.srcpath}'.", file=sys.stderr)
        sys.exit(2)

    html_files = [f for f in args.srcpath.glob("*.html") if f.is_file()]

    if not html_files:
        print(f"Ошибка: Нет файлов для рендера в папке '{args.srcpath}'.",
              file=sys.stderr)
        sys.exit(3)

    unreadable_files = []
    for file in html_files:
        if not os.access(file, os.R_OK):
            unreadable_files.append(file)

    if unreadable_files:
        print("Ошибка: Нет доступа на чтение следующих файлов для рендера:",
              file=sys.stderr)
        for file in unreadable_files:
            print(f" - {file}", file=sys.stderr)
        print("Рендеринг невозможен.", file=sys.stderr)
        sys.exit(4)

    if args.outpath.exists():
        shutil.rmtree(args.outpath)

    site = Site.make_site(
        searchpath=args.srcpath,
        outpath=args.outpath,
        contexts=[(".*.html", get_context)],
    )

    site.render(use_reloader=args.watch)

    assets_src = Path("assets")
    assets_dest = args.outpath / "assets"

    if assets_src.exists():
        shutil.copytree(assets_src, assets_dest, dirs_exist_ok=True)

    js_src = Path("app.js")
    if js_src.exists():
        shutil.copy(js_src, args.outpath / "app.js")


if __name__ == "__main__":
    main()
