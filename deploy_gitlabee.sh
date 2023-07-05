docker build -t gitlab-ee:crake .
# export GITLAB_HOME=/gitlab
# mkdir -p $GITLAB_HOME
docker run --detach \
  --hostname 127.0.0.1:80 \
  --publish 80:80 \
  --name gitlab \
  --restart always \
  --volume $GITLAB_HOME/config:/etc/gitlab \
  --volume $GITLAB_HOME/logs:/var/log/gitlab \
  --volume $GITLAB_HOME/data:/var/opt/gitlab \
  gitlab-ee:crake
  # --shm-size 256m \
# cat $GITLAB_HOME/config/initial_root_password