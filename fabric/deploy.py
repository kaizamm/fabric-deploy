#!/usr/bin/python
# encoding: utf-8

from fabric.api import *
import yaml

env.timeout=30
env.warn_only=True
env.parallel=False
global config # 装载YAML配置的对象
global target # 操作目标，对应YAML配置中的项目名称
global target_env # 操作目标的环境，对应YAML配置中项目下的环境
global target_app_role_name # 操作目标对应APP应用的角色名称，用于和env.roledefs相关联
global target_nginx_role_name # 操作目标对应nginx的角色名称，用于和env.roledefs相关联

# 从YAML文件加载配置初始化环境变量
def load_config(**kwargs):
  try:
      global config, target, target_env, target_app_role_name, target_nginx_role_name
      config = yaml.load(file('/usr/fabric/env.yaml'))
      target = kwargs['target']
      target_env = kwargs['env']
      target_app_role_name = '%s-%s-app' % (target, target_env)
      if 'nginx' in config[target][target_env]:
        target_nginx_role_name = '%s-%s-nginx' % (target, target_env)
  except yaml.YAMLError, e:
    print "Error in configuration file:", e
    abort("[LOAD CONFIG] Aborting at user request.")
      
  
  env.roledefs = config['fab.env.roledefs']
  env.passwords = config['fab.env.passwords']
  print(env.roledefs)
  print(env.passwords)
  print('target:%s' % target)
  print('env:%s' % target_env)
  print('app_role:%s' % target_app_role_name)
  if 'nginx' in config[target][target_env]:
    print('nginx_role:%s' % target_nginx_role_name)

# nginx中下线指定主机
def offline(**kwargs):
  print('[OFFLINE] <<<<<<<<<<<<< env.host_string: #%s# <<<<<<<<<<<<<' % env.host_string)

  daemon = config[target][target_env]['nginx'][env.host_string]['daemon']
  conf = config[target][target_env]['nginx'][env.host_string]['conf']
  app_host = kwargs['app_host']
  app_port = kwargs['app_port']
  #remote_script = "config[target][target_env]['nginx']['action']['down'] conf daemon app_host app_port"
  remote_script = config[target][target_env]['nginx']['action']['down']
  print('[OFFLINE] daemon: #%s#' % daemon)
  print('[OFFLINE] conf: #%s#' % conf)
  print('[OFFLINE] app_host: #%s#' % app_host)
  print('[OFFLINE] app_port: #%s#' % app_port)
  print('[OFFLINE] remote_script: #%s#' % remote_script)

  ret=run('echo "[OFFLINE] `hostname`"')
  args = '"%s" "%s" "%s" "%s"' % (conf, daemon, app_host, app_port)
  print("CMD=#%s#" % remote_script)
  print("ARGS=#%s#" % args)
  ret=run('%s %s' % (remote_script, args))
  if ret.failed:
    print(ret.return_code)
    abort('[OFFLINE] Aborting at user request.')

# nginx中上线指定主机
def online(**kwargs):
  print('[ONLINE] <<<<<<<<<<<<< env.host_string: #%s# <<<<<<<<<<<<<' % env.host_string)

  daemon = config[target][target_env]['nginx'][env.host_string]['daemon']
  conf = config[target][target_env]['nginx'][env.host_string]['conf']
  app_host = kwargs['app_host']
  app_port = kwargs['app_port']
  remote_script = config[target][target_env]['nginx']['action']['up']
  print('[ONLINE] daemon: #%s#' % daemon)
  print('[ONLINE] conf: #%s#' % conf)
  print('[ONLINE] app_host: #%s#' % app_host)
  print('[ONLINE] app_port: #%s#' % app_port)
  print('[ONLINE] remote_script: #%s#' % remote_script)

  args = '"%s" "%s" "%s" "%s"' % (conf, daemon, app_host, app_port)
  print("CMD=#%s#" % remote_script)
  print("ARGS=#%s#" % args)
  ret=run('chmod +x ~/deploy -R')
  ret=run('%s %s' % (remote_script, args))
  if ret.failed:
    print(ret.return_code)
    abort('[ONLINE] Aborting at user request.')

# 常规发布
def update(**kwargs):
  print('[UPDATE] <<<<<<<<<<<<< env.host_string: #%s# <<<<<<<<<<<<<' % env.host_string)

  tomcat_home = config[target][target_env]['apps'][env.host_string]['tomcat_home']
  host = config[target][target_env]['apps'][env.host_string]['host']
  dir_update = config[target][target_env]['apps'][env.host_string]['dir_update']
  dir_dest = config[target][target_env]['apps'][env.host_string]['dir_dest'] 
  dir_src = config[target][target_env]['apps'][env.host_string]['dir_src']
  app_name = config[target][target_env]['apps'][env.host_string]['APP_NAME']
  url = config[target][target_env]['apps'][env.host_string]['CHECK_URL']
  action = kwargs['action']
  
  remote_script = config[target][target_env]['apps']['action']['deploy']

  print('[UPDATE] tomcat_home: #%s#' % tomcat_home)
  print('[UPDATE] host: #%s#' % host)
  print('[UPDATE] remote_script: #%s#' % remote_script)
  
  args = '--ACTION %s --TOMCAT_HOME %s  --APP_NAME %s --dir_src  %s --dir_dest %s --dir_update %s --CHECK_URL %s' % (action, tomcat_home, app_name, dir_src, dir_dest, dir_update, url)
  print("CMD=#%s#" % remote_script)
  print("ARGS=#%s#" % args)
  ret=run('%s %s' % (remote_script, args))
  if ret.failed:
    print(ret.return_code)
    abort('[UPDATE] Aborting at user request.')

# 文件上传
#@parallel(pool_size=5)
def upload(**kwargs):
  print('[UPLOAD] <<<<<<<<<<<<< %s@%s <<<<<<<<<<<<<' % (env.user, env.host))
  local_deploy_home=config[target][target_env]['upload']['local_deploy_home']
  remote_deploy_home=config[target][target_env]['upload']['remote_deploy_home']
  local_target_path=config[target][target_env]['upload']['local_target_path']
  remote_update_path=config[target][target_env]['upload']['remote_update_path']
  run('rm -rf %s' % remote_deploy_home)
  run('rm -rf %s' % remote_update_path)
  run('mkdir -p %s' % remote_update_path)
  ret=put(local_path=local_deploy_home, remote_path=remote_deploy_home)
  if ret.failed:
    abort("[UPLOAD] Aborting at user request.")
  ret=put(local_path=local_target_path, remote_path=remote_update_path)
  if ret.failed:
    abort("[UPLOAD] Aborting at user request.")

def deploy(*args,**kwargs):
  # Upload
  print('[UPLOAD] <<<<<<<<<<<<< %s@%s <<<<<<<<<<<<<' % (env.user, env.host))
  ret=execute(upload, roles=['%s-%s-app' % (target, target_env)],)
  for target_host in env.roledefs[target_app_role_name]:
    print('<<<<<<<<<<<<< [DEPLOY] HOST: %s' % target_host)

    app_host = config[target][target_env]['apps'][target_host]['host']
    app_port = config[target][target_env]['apps'][target_host]['port']

    # Offline
    if 'nginx' in config[target][target_env]:
      execute(offline, roles=[target_nginx_role_name], app_host=app_host, app_port=app_port)
  
    # Deploy
    execute(update, hosts=[target_host], action=kwargs['action'])
  
    # Online
    if 'nginx' in config[target][target_env]:
      execute(online, roles=[target_nginx_role_name], app_host=app_host, app_port=app_port)

