### init
library(RPostgres)
library(tidyverse)
library(fs)
library(zoo)
library(httr)
library(boxr)
library(jose)

### directory check
print("print getwd")
print(getwd())
print("List files of wd")
print(list.files(getwd()))
write.csv(
  data.frame(A = Sys.time(), B = "A", C = 1),
  file = paste0(getwd(), "/.github/Git-datafiles/existing.csv")
)

### db conn
print("1. db connection")
cl_cert <- "hwang_git.crt"
cl_key <- "hwang_git.key"

con <- dbConnect(
  RPostgres::Postgres(),
  dbname = "mbta_dw",
  host = "mbta01.mghpcc.org",
  port = "5432",
  user = "hwang",
  sslcert = cl_cert, 
  sslkey = cl_key)
print("    db connection successful")

### set query parameters
print("2. perform query")
thisday <- today()
start_date <- floor_date(thisday, unit = "month") - months(1) ## should be minus 1 month
start_date_next <- lubridate::ceiling_date(start_date, unit = "month")
recent_start_date <- seq(start_date_next, length = 3, by = "-1 year")[3]

### SQL query
gse <- dbGetQuery(con, gsub("\r?\n|\r", " ",
                            paste0(
                              "WITH gated1 AS (
SELECT servicedate as service_date,
CONCAT('(', RIGHT(halfhour::varchar, 8), ')') as time_period,
CASE WHEN stationname IN ('Alewife') THEN 'place-alfcl'
WHEN stationname IN ('Andrew') THEN 'place-andrw'
WHEN stationname IN ('Airport') THEN 'place-aport'
WHEN stationname IN ('Aquarium') THEN 'place-aqucl'
WHEN stationname IN ('Arlington') THEN 'place-armnl'
WHEN stationname IN ('Ashmont') THEN 'place-asmnl'
WHEN stationname IN ('Assembly') THEN 'place-astao'
WHEN stationname IN ('Back Bay') THEN 'place-bbsta'
WHEN stationname IN ('Beachmont') THEN 'place-bmmnl'
WHEN stationname IN ('Bowdoin') THEN 'place-bomnl'
WHEN stationname IN ('Boylston') THEN 'place-boyls'
WHEN stationname IN ('Broadway') THEN 'place-brdwy'
WHEN stationname IN ('Braintree') THEN 'place-brntn'
WHEN stationname IN ('Community College') THEN 'place-ccmnl'
WHEN stationname IN ('Charles/MGH') THEN 'place-chmnl'
WHEN stationname IN ('Chinatown') THEN 'place-chncl'
WHEN stationname IN ('Central') THEN 'place-cntsq'
WHEN stationname IN ('Copley') THEN 'place-coecl'
WHEN stationname IN ('Courthouse') THEN 'place-crtst'
WHEN stationname IN ('Davis') THEN 'place-davis'
WHEN stationname IN ('Downtown Crossing') THEN 'place-dwnxg'
WHEN stationname IN ('Fields Corner') THEN 'place-fldcr'
WHEN stationname IN ('Forest Hills') THEN 'place-forhl'
WHEN stationname IN ('Government Center') THEN 'place-gover'
WHEN stationname IN ('Green Street') THEN 'place-grnst'
WHEN stationname IN ('Haymarket') THEN 'place-haecl'
WHEN stationname IN ('Harvard') THEN 'place-harsq'
WHEN stationname IN ('Hynes Convention Center') THEN 'place-hymnl'
WHEN stationname IN ('Jackson Square') THEN 'place-jaksn'
WHEN stationname IN ('JFK/Umass') THEN 'place-jfk'
WHEN stationname IN ('Kenmore') THEN 'place-kencl'
WHEN stationname IN ('Kendall/MIT') THEN 'place-knncl'
WHEN stationname IN ('Lechmere') THEN 'place-lech'
WHEN stationname IN ('Massachusetts Ave.') THEN 'place-masta'
WHEN stationname IN ('Malden Center') THEN 'place-mlmnl'
WHEN stationname IN ('Maverick') THEN 'place-mvbcl'
WHEN stationname IN ('North Station') THEN 'place-north'
WHEN stationname IN ('North Quincy') THEN 'place-nqncy'
WHEN stationname IN ('Oak Grove') THEN 'place-ogmnl'
WHEN stationname IN ('Orient Heights') THEN 'place-orhte'
WHEN stationname IN ('Park Street') THEN 'place-pktrm'
WHEN stationname IN ('Porter') THEN 'place-portr'
WHEN stationname IN ('Prudential') THEN 'place-prmnl'
WHEN stationname IN ('Quincy Adams') THEN 'place-qamnl'
WHEN stationname IN ('Quincy Center') THEN 'place-qnctr'
WHEN stationname IN ('Revere Beach') THEN 'place-rbmnl'
WHEN stationname IN ('Roxbury Crossing') THEN 'place-rcmnl'
WHEN stationname IN ('Riverside') THEN 'place-river'
WHEN stationname IN ('Ruggles') THEN 'place-rugg'
WHEN stationname IN ('Stony Brook') THEN 'place-sbmnl'
WHEN stationname IN ('Suffolk Downs') THEN 'place-sdmnl'
WHEN stationname IN ('Savin Hill') THEN 'place-shmnl'
WHEN stationname IN ('Shawmut') THEN 'place-smmnl'
WHEN stationname IN ('Science Park') THEN 'place-spmnl'
WHEN stationname IN ('South Station') THEN 'place-sstat'
WHEN stationname IN ('State Street') THEN 'place-state'
WHEN stationname IN ('Sullivan Square') THEN 'place-sull'
WHEN stationname IN ('Symphony') THEN 'place-symcl'
WHEN stationname IN ('Tufts Medical Center') THEN 'place-tumnl'
WHEN stationname IN ('Wellington') THEN 'place-welln'
WHEN stationname IN ('Wood Island') THEN 'place-wimnl'
WHEN stationname IN ('Wollaston') THEN 'place-wlsta'
WHEN stationname IN ('Wonderland') THEN 'place-wondl'
WHEN stationname IN ('World Trade Center') THEN 'place-wtcst'
END AS stop_id,
CASE WHEN stationname IN ('JFK/Umass') THEN 'JFK/UMass'
WHEN stationname IN ('Charles MGH') THEN 'Charles/MGH'
WHEN stationname IN ('Massachusetts Ave.') THEN 'Massachusetts Avenue'
ELSE stationname
END AS station_name,
route_or_line,
CASE WHEN stationname IN ('Downtown Crossing', 'State Street', 'Haymarket', 'North Station', 'Government Center', 'South Station', 'Park Street')
THEN 1
ELSE 0
END AS split_ind,
SUM(rawtaps_split) as gated_entries
from ridership.tableau_r r
WHERE route_or_line LIKE ('%Line')
AND stationname NOT LIKE ('%Garage')
AND r.servicedate >= '", as.character(recent_start_date), "'
AND r.servicedate < '", as.character(start_date_next), "'
GROUP BY 1,2,3,4,5,6
ORDER BY 1 DESC,2,3)

SELECT
service_date,
time_period,
stop_id,
station_name,
route_or_line,
CASE WHEN split_ind = 1 THEN ROUND(gated_entries,2)
ELSE gated_entries
END as gated_entries
FROM gated1")))
dbDisconnect(con)

### connect to Box
box_token <- "BOX_TOKEN.json"
box_auth_service(token_file = box_token)
box_setwd("113530111731") # manager review folder
box_ls()

### Save raw file
rawfilename = paste0(tempdir(), "/", format(start_date,"%Y-%m"), "_GatedStationEntries_recent.csv")
write_csv(gse, file = rawfilename)
box_ul(file = rawfilename, dir_id = "162420304672")
file_delete(rawfilename)


### Save Data File
DataFileName <- paste0(tempdir(), "/", format(start_date,"%Y-%m"), "_GatedStationEntries.csv")
write_csv(gse, file = DataFileName)
box_ul(file = DataFileName)
file_delete(DataFileName)



##Run QA
if(TRUE){
print("4. run QA script")
filename_QA <- paste0(getwd(), "/Current Scripts/Gated Station Entries/QA_gse.qmd")
temp_output_dir <- paste0(tempdir(), "/", format(start_date,"%Y-%m"), "_GSE_qa.html")
quarto::quarto_render(
  input = filename_QA,
  execute_dir = temp_output_dir
)
box_ul(file = temp_output)
}




