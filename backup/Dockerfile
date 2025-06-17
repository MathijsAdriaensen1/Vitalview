FROM postgres:15
RUN apt-get update && apt-get install -y cron
COPY cronjob.sh /cronjob.sh
RUN chmod +x /cronjob.sh
RUN echo "0 * * * * /cronjob.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/backup-cron
RUN crontab /etc/cron.d/backup-cron
CMD ["cron", "-f"]