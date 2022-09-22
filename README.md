# Log Analyzer

Скрипт для анализа логов по $request_time (в nginx
http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format)

## Использование

```shell
python log_analyzer.py --config ../path-to-config.json
```

Параметр --config указывает на json файл конфигурации скрипта(пример - config.json).
Является необязательным, при его отсутствии используется стандартная конфигурация, указанная ниже.

## Стандартная конфигурация

**REPORT_SIZE** - Количество строк отчета, выводимых в результирующем html-файле  
**REPORT_DIR** - Путь до каталога, в который будут сохранятся отчеты.
Если по последнему логу в LOG_DIR уже существует отчет - то в логах скрипта выводится предупреждение и работа
завершается без повторного парсинга.  
**LOG_DIR** - Путь до папки с логами, в которой будет найден и распаршен последний по дате отчет.
Формат имени файла лога, которые подлежат анализу - nginx-access-ui.log-YYYYMMDD, где YYYYMMDD - дата создания лога.
Лог может быть в формате gz или plain text.  
**LOG_FILE** - имя файла логов, в который будут сохранятся логи скрипта log-analyzer.py. При отсутсвии работа скрипта
логируется в консоли.  
**ERROR_THRESHOLD** - доля допустимых ошибок - число в диапазоне [0..1] обозначающее долю нераспаршенных строк в отчете. 
Если по каким-то причинам был сменен формат логирования, новые строки логов будут считаться ошибочными.  
**REPORT_TEMPLATE_PATH** - путь до шаблона отчета report.html  

```json
{
  "REPORT_SIZE": 10,
  "REPORT_DIR": "./reports",
  "LOG_DIR": "./log",
  "LOG_FILE": "",
  "ERROR_THRESHOLD": 0.5,
  "REPORT_TEMPLATE_PATH": "report.html"
}
```

## Формат строки лог-файлов, допустимых к анализу
```text
 log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
                     '$status $body_bytes_sent "$http_referer" '
                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
                     '$request_time';
```

## Тестирование

todo