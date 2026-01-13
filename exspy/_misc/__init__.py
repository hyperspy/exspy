# -*- coding: utf-8 -*-
# Copyright 2007-2025 The eXSpy developers
#
# This file is part of eXSpy.
#
# eXSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eXSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with eXSpy. If not, see <https://www.gnu.org/licenses/#GPL>.

from time import sleep


def _download_GOS_files(download_all=True):
    """
    Download GOS files for testing purposes and building documentation.

    Parameters
    ----------
    download_all : bool, optional
        If True, download all GOS files. If False, download only recent GOS files.
        Default is True.
    """
    import pooch

    def retry_and_sleep(url, known_hash, retries=3, sleep_time=30):
        for attempt in range(retries):
            try:
                return pooch.retrieve(
                    url=url,
                    known_hash=known_hash,
                    # use large chunk size to reduce number of requests to Zenodo
                    downloader=pooch.HTTPDownloader(chunk_size=30000),
                    progressbar=False,
                )
            except Exception as e:
                if attempt < retries - 1:
                    print(
                        f"Download failed (attempt {attempt + 1}/{retries}). "
                        f"Retrying in {sleep_time} seconds..."
                    )
                    sleep(sleep_time)
                else:
                    print("All download attempts failed.")
                    raise e

    print("Checking if GOS files need downloading...")
    retry_and_sleep(
        url="https://zenodo.org/records/7645765/files/Segger_Guzzinati_Kohl_1.5.0.gosh",
        known_hash="md5:7fee8891c147a4f769668403b54c529b",
    )
    if download_all:
        retry_and_sleep(
            url="https://zenodo.org/records/12800856/files/Dirac_GOS_compact.gosh",
            known_hash="md5:01a855d3750d2c063955248358dbee8d",
        )
        retry_and_sleep(
            url="https://zenodo.org/records/6599071/files/Segger_Guzzinati_Kohl_1.0.0.gos",
            known_hash="md5:d65d5c23142532fde0a80e160ab51574",
        )
    print("GOS files available.")


__all__ = [
    "_download_GOS_files",
]


def __dir__():
    return sorted(__all__)
