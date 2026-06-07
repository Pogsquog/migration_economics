# Source Data Manifest

Downloaded on 2026-06-07 for re-analysis of `dp16472.pdf`:

Nam, Hoseong and Portes, Jonathan. "Migration and Productivity in the UK: An Analysis of Employee Payroll Data." IZA DP No. 16472, September 2023.

To recreate these files, run:

```sh
bash scripts/download_sources.sh
```

## Core Regression Inputs

### HMRC PAYE RTI / Migrant Worker Scan employment data

Paper reference: HM Revenue & Customs (2023), "UK payrolled employments by nationality, region and industry, from July 2014 to June 2021".

Landing page:
https://www.gov.uk/government/statistics/payrolled-employments-in-the-uk-by-region-industry-and-nationality-from-july-2014-to-june-2021

Downloaded file:
`Payrolled_employments_in_the_UK_by_region__industry_and_nationality__July_2014_to_June_2021.xlsx`

Source URL:
https://assets.publishing.service.gov.uk/media/641c49b032a8e0000cfa92d1/Payrolled_employments_in_the_UK_by_region__industry_and_nationality__July_2014_to_June_2021.xlsx

SHA-256:
`7843b1ae0751723823cb92424103b400b18d9514ab67c77134f62a48f78fafc9`

### ONS labour productivity by industry and region

Paper reference: Office for National Statistics (2021), "Region by industry labour productivity".

Landing page:
https://www.ons.gov.uk/economy/economicoutputandproductivity/productivitymeasures/datasets/industrybyregionlabourproductivity

Downloaded file:
`ons_region_by_industry_labour_productivity_1998_to_2019_indbyreg.xls`

Source URL:
https://www.ons.gov.uk/file?uri=/economy/economicoutputandproductivity/productivitymeasures/datasets/industrybyregionlabourproductivity/1998to2019/indbyreg.xls

SHA-256:
`38033212ac6510cd9dc8e381e970a3c36619251bd4b5ab8e0913cba5e3a03563`

Note: the ONS page's JSON-LD `current` URL points to `/current/indbyreg.xls`, which returned 404 on 2026-06-07. The visible "1998 to 2019" edition-specific URL downloaded successfully and matches the coverage described in the paper.

## Related / Update Inputs

### HMRC December 2022 update

Landing page:
https://www.gov.uk/government/statistics/uk-payrolled-employments-by-nationality-region-and-industry-from-july-2014-to-december-2022

Downloaded file:
`Payrolled_employments_in_the_UK_by_region__industry_and_nationality__from_July_2014_to_December_2022_Data_tables.ods`

Source URL:
https://assets.publishing.service.gov.uk/media/641c3c355155a200136ad514/Payrolled_employments_in_the_UK_by_region__industry_and_nationality__from_July_2014_to_December_2022_-_Data_tables.ods

SHA-256:
`2affdaa110df9e2cba8519729a668419c6180d3ebb14cf89de7b0f9bbcb9beeb`

### ONS PAYE RTI NUTS1 region and nationality data

Paper reference: Office for National Statistics (2023), "Employments from Pay As You Earn Real Time Information: ad hoc estimates of payrolled employees by NUTS1 region and nationality".

Landing page:
https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted

Downloaded files:

- `ons_nuts1_by_nationality_nsa_and_sa_mar2023.xlsx`
  - Source URL: https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted/march2023/nuts1bynationalitynsaandsamar2023.xlsx
  - SHA-256: `49d7e40c6fe8c455cf8134ebbf5786d905af5c02a32c74495572f1ef974a2e7d`

- `ons_nuts1_by_nationality_nsa_and_sa_mar2022.xlsx`
  - Source URL: https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted/march2022/nuts1bynationalitynsaandsamar2022.xlsx
  - SHA-256: `180334317b211116836b78b5449a28a112312ced96050a8db64e55f13ce483ed`

- `ons_mws_rti_data_seasonally_adjusted_march2021.xlsx`
  - Source URL: https://www.ons.gov.uk/file?uri=/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/employmentsfrompayasyouearnrealtimeinformationadhocestimatesofpayrolledemployeesbynuts1regionandnationalityseasonallyadjusted/march2021/mwsrtidataseasonallyadjustedmarch211.xlsx
  - SHA-256: `74f770b5c78ba5c3fc6ad255115baf441e66d679a49d614e2a78ef6d6839668c`
