### init
library(RPostgres)
library(tidyverse)
library(fs)
library(lubridate)
library(boxr)
library(jose)

### directory check
print("print getwd")
print(getwd())
print("List files of wd")
print(list.files(getwd()))
write_csv(
  data.frame(A = Sys.time(), B = "A", C = 1),
  file = paste0(getwd(), "/.github/Git-datafiles/existing.csv")
)

### db conn
print("1. db connection")
cl_cert <- "hwang_git.crt"
cl_key <- "hwang_git.key"
con <- dbConnect(
  Postgres(),
  dbname = "mbta_dw",
  host = "mbta01.mghpcc.org",
  port = "5432",
  user = "hwang",
  sslcert = cl_cert,
  sslkey = cl_key
)
print("    db connection successful")


### Setup Query
print("2. perform query")
thisday <- today()
start_date <- floor_date(thisday, unit = "month") - months(1)
#import data
csat_all <- dbGetQuery(con, paste0(
  "SELECT DISTINCT 
	survey_date, 
	survey_name, 
	question_description, 
	response_total, 
	response_1_text, 
	round(response_1_percent, 2) AS response_1_percent,
	response_2_text, 
	round(response_2_percent, 2) AS response_2_percent, 
	response_3_text, 
	round(response_3_percent, 2) AS response_3_percent, 
	response_4_text, 
	round(response_4_percent, 2) AS response_4_percent, 
	response_5_text, 
	round(response_5_percent, 2) AS response_5_percent, 
	response_6_text, 
	round(response_6_percent, 2) AS response_6_percent, 
	response_7_text, 
	round(response_7_percent, 2) AS response_7_percent 
FROM surveys.dashboard_survey_result_archive r 
LEFT JOIN surveys.dashboard_survey_response_type_archive t 
ON r.response_type_id = t.response_type_id 
LEFT JOIN surveys.dashboard_survey_questions_archive q 
ON r.question_id = q.question_id 
WHERE r.archive_time = (
    SELECT max(archive_time) 
    FROM surveys.dashboard_survey_result_archive
)
AND r.question_id IN (3, 4, 10, 31) 
ORDER BY survey_date;"
))
dbDisconnect(con)
rm(con)

### connect to Box
box_token <- "BOX_TOKEN.json"
box_auth_service(token_file = box_token)
box_setwd("113530111731") # manager review folder
box_ls()

### Save result csv
print("3. save result csv")
#csat <- csat_all %>% filter(survey_date == start_date)
result_filename <- paste0(tempdir(), "/", format(start_date,"%Y-%m"), "_csat.csv")
write_csv(csat_all, file = result_filename)
box_ul(file = result_filename)
file_delete(result_filename)

##Run QA
if(FALSE){
print("4. run QA script")
filename_QA <- paste0(getwd(), "/Current Scripts/CSAT/QA_csat.qmd")
temp_output_dir <- tempdir()
writeLines(getwd(), con = paste0(temp_output_dir, "/github_directory.txt"))
temp_output <- paste0(temp_output_dir, "/QA_csat_output")
quarto::quarto_render(
  input = filename_QA,
  execute_dir = temp_output
)
box_ul(file = temp_output)
}