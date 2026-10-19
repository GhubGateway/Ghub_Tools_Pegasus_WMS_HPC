# Configuration file for jupyter-notebook.

#c = get_config()  #noqa

#------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
#------------------------------------------------------------------------------

## This is an application.

## The default URL to redirect to from `/`
#  Default: '/tree'
# c.NotebookApp.default_url = '/tree'
# Appmode (https://github.com/oschuett/appmode):
c.NotebookApp.default_url = '/apps/askiced.ipynb'
# Edit mode: 
# c.NotebookApp.default_url = '/notebooks/askiced.ipynb'

## (bytes/sec)
#          Maximum rate at which stream output can be sent on iopub before they are
#          limited.
#  Default: 1000000
#c.NotebookApp.iopub_data_rate_limit = 1000000
# Increase IOPub data rate (Crucial for large ipywidget file uploads)
c.NotebookApp.iopub_data_rate_limit = 1000000000.0  # 1GB/s

## (msgs/sec)
#          Maximum rate at which messages can be sent on iopub before they are
#          limited.
#  Default: 1000
# c.NotebookApp.iopub_msg_rate_limit = 1000
c.NotebookApp.iopub_msg_rate_limit = 1000000.0  # .001GB/s

## The IP address the notebook server will listen on.
#  Default: 'localhost'
# c.NotebookApp.ip = 'localhost'

### Sets the maximum allowed size of the client request body, specified in the
#  Content-Length request header field. If the size in a request exceeds the
#  configured value, a malformed HTTP message is returned to the client.
#  
#  Note: max_body_size is applied even in streaming mode.
#  Default: 536870912
#c.NotebookApp.max_body_size = 536870912

## Gets or sets the maximum amount of memory, in bytes, that is allocated for use
#  by the buffer manager.
#  Default: 536870912
#c.NotebookApp.max_buffer_size = 536870912

## The directory to use for notebooks and kernels.
#  Default: ''
# c.NotebookApp.notebook_dir = ''

## The port the notebook server will listen on (env: JUPYTER_PORT).
#  Default: 8888
# c.NotebookApp.port = 8888

## (sec) Time window used to
#          check the message and data rate limits.
#  Default: 3
# c.NotebookApp.rate_limit_window = 3

## Supply SSL options for the tornado HTTPServer.
#              See the tornado docs for details.
#  Default: {}
# c.NotebookApp.ssl_options = {}

## Supply overrides for the tornado.web.Application that the Jupyter notebook
#  uses.
#  Default: {}
#c.NotebookApp.tornado_settings = {}
# 400 MiB = 400*1024*1024 = 419430400
c.NotebookApp.tornado_settings = {
    "websocket_max_message_size": 419430400,
    "max_body_size": 419430400,
    "max_buffer_size": 419430400
}
