#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${ROOT_DIR}/data/sources"

mkdir -p "${SOURCE_DIR}"

download() {
  local filename="$1"
  local url="$2"
  local expected_sha="$3"
  local path="${SOURCE_DIR}/${filename}"
  local tmp="${path}.tmp"

  printf 'Downloading %s\n' "${filename}"
  curl -fL --retry 3 --retry-delay 2 -o "${tmp}" "${url}"

  local actual_sha
  actual_sha="$(sha256sum "${tmp}" | awk '{print $1}')"
  if [[ "${actual_sha}" != "${expected_sha}" ]]; then
    printf 'Checksum mismatch for %s\n' "${filename}" >&2
    printf 'Expected: %s\n' "${expected_sha}" >&2
    printf 'Actual:   %s\n' "${actual_sha}" >&2
    rm -f "${tmp}"
    exit 1
  fi

  mv "${tmp}" "${path}"
}

download \
  "Payrolled_employments_in_the_UK_by_region__industry_and_nationality__July_2014_to_June_2021.xlsx" \
  "https://assets.publishing.service.gov.uk/media/641c49b032a8e0000cfa92d1/Payrolled_employments_in_the_UK_by_region__industry_and_nationality__July_2014_to_June_2021.xlsx" \
  "7843b1ae0751723823cb92424103b400b18d9514ab67c77134f62a48f78fafc9"

download \
  "Payrolled_employments_in_the_UK_by_region__industry_and_nationality__from_July_2014_to_December_2022_Data_tables.ods" \
  "https://assets.publishing.service.gov.uk/media/641c3c355155a200136ad514/Payrolled_employments_in_the_UK_by_region__industry_and_nationality__from_July_2014_to_December_2022_-_Data_tables.ods" \
  "2affdaa110df9e2cba8519729a668419c6180d3ebb14cf89de7b0f9bbcb9beeb"

download \
  "ons_region_by_industry_labour_productivity_1998_to_2019_indbyreg.xls" \
  "https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/productivitymeasures/datasets/industrybyregionlabourproductivity/1998to2019/indbyreg.xls" \
  "38033212ac6510cd9dc8e381e970a3c36619251bd4b5ab8e0913cba5e3a03563"

download \
  "ons_nuts1_by_nationality_nsa_and_sa_mar2023.xlsx" \
  "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted/march2023/nuts1bynationalitynsaandsamar2023.xlsx" \
  "49d7e40c6fe8c455cf8134ebbf5786d905af5c02a32c74495572f1ef974a2e7d"

download \
  "ons_nuts1_by_nationality_nsa_and_sa_mar2022.xlsx" \
  "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted/march2022/nuts1bynationalitynsaandsamar2022.xlsx" \
  "180334317b211116836b78b5449a28a112312ced96050a8db64e55f13ce483ed"

download \
  "ons_mws_rti_data_seasonally_adjusted_march2021.xlsx" \
  "https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted/march2021/mwsrtidataseasonallyadjustedmarch211.xlsx" \
  "74f770b5c78ba5c3fc6ad255115baf441e66d679a49d614e2a78ef6d6839668c"

printf 'Downloaded and verified source data in %s\n' "${SOURCE_DIR}"
