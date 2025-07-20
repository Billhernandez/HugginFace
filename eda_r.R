# Este archivo puede usarse si prefieres lanzar EDA por línea de comandos
df <- read.csv("data.csv")
sink("eda_r_report.txt")
summary(df)
sink()
