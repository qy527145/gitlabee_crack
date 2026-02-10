## 运行python脚本，生成GitLabEE.gitlab-license等认证相关文件
```
pip install -r requirements.txt
python gitlab_crack.py
```
## 部署gitlab-ee，等待端口启动
```
export GITLAB_HOME=/gitlab
rm -rf $GITLAB_HOME
mkdir -p $GITLAB_HOME
sh deploy_gitlabee.sh
```
## 等待服务启动后，访问[首页](http://127.0.0.1)，账号root，密码使用下面命令获取
```
cat $GITLAB_HOME/config/initial_root_password
```
## 随后进入[管理员设置](http://127.0.0.1/admin/application_settings/general)上传GitLabEE.gitlab-license激活即可

## 全流程激活示例
```bash
docker pull docker.1ms.run/gitlab/gitlab-ee:17.11.7-ee.0
docker run -d -p 5080:80 --name gitlab docker.1ms.run/gitlab/gitlab-ee:17.11.7-ee.0
docker exec -it gitlab cat /etc/gitlab/initial_root_password
uv run gitlab_crack.py
docker cp .license_encryption_key.pub gitlab:/opt/gitlab/embedded/service/gitlab-rails/.license_encryption_key.pub
docker exec -it gitlab gitlab-ctl restart
docker stop gitlab
docker rm gitlab
```
