"""
Приведение входного файла (doc / docx / pdf) к формату, с которым умеет
работать соответствующий парсер.

Единственный особый случай — legacy .doc: у него нет питоновской
библиотеки уровня python-docx, поэтому он предварительно
конвертируется в .docx через LibreOffice в headless-режиме.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SUPPORTED_EXTENSIONS = {".doc", ".docx", ".pdf"}


class UnsupportedFormatError(ValueError):
    pass


class ConversionError(RuntimeError):
    pass


def _find_soffice() -> str:
    """
    Находит исполняемый файл LibreOffice в системе.
    Сначала проверяет переменную окружения, потом стандартные пути.
    """
    # 1. Проверяем переменную окружения
    soffice_path = os.environ.get("LIBREOFFICE_PATH")
    if soffice_path and os.path.exists(soffice_path):
        try:
            subprocess.run([soffice_path, "--version"],
                           capture_output=True,
                           check=True)
            return soffice_path
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # 2. Ищем в PATH
    soffice = shutil.which("soffice")
    if soffice:
        try:
            subprocess.run([soffice, "--version"],
                           capture_output=True,
                           check=True)
            return soffice
        except subprocess.CalledProcessError:
            pass

    # 3. Проверяем стандартные пути для Linux (в контейнере)
    linux_paths = [
        "/usr/bin/soffice",
        "/usr/lib/libreoffice/program/soffice",
        "/opt/libreoffice/program/soffice",
    ]
    for path in linux_paths:
        if os.path.exists(path):
            try:
                subprocess.run([path, "--version"],
                               capture_output=True,
                               check=True)
                return path
            except subprocess.CalledProcessError:
                pass

    # 4. Проверяем пути для Windows (для локальной разработки)
    windows_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for path in windows_paths:
        if os.path.exists(path):
            return path

    raise RuntimeError(
        "LibreOffice не найден! Установите LibreOffice или укажите путь "
        "через переменную окружения LIBREOFFICE_PATH."
    )


def detect_format(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Формат '{ext}' не поддерживается. Ожидается: {sorted(SUPPORTED_EXTENSIONS)}"
        )
    return ext


def ensure_docx(path: str, workdir: str | None = None) -> str:
    """
    Если path указывает на .doc — конвертирует его в .docx через
    LibreOffice и возвращает путь к новому файлу. Для .docx возвращает
    исходный путь без изменений.

    workdir — куда положить результат конвертации; по умолчанию
    системная временная директория.
    """
    ext = Path(path).suffix.lower()
    if ext == ".docx":
        return path
    if ext != ".doc":
        raise UnsupportedFormatError(f"ensure_docx не поддерживает {ext}")

    out_dir = workdir or tempfile.mkdtemp(prefix="tp_doc2docx_")
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    soffice_cmd = _find_soffice()

    # --headless обязателен: soffice без него пытается поднять GUI/сокеты,
    # которые в песочнице без сети недоступны и процесс подвисает.
    proc = subprocess.run(
        [
            soffice_cmd,
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            out_dir,
            path,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise ConversionError(
            f"Не удалось сконвертировать {path} в docx: {proc.stderr or proc.stdout}"
        )

    converted = Path(out_dir) / (Path(path).stem + ".docx")
    if not converted.exists():
        raise ConversionError(
            f"LibreOffice отчитался об успехе, но файл {converted} не найден"
        )
    return str(converted)