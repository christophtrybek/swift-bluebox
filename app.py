"""
    Project Bluebox
    2015, University of Stuttgart, IPVS/AS
"""
"""
    Project Bluebox

    Copyright (C) <2015> <University of Stuttgart>

    This software may be modified and distributed under the terms
    of the MIT license.  See the LICENSE file for details.
"""
# initialize logging

from functools import wraps
from datetime import datetime
import json, logging, os, time
import sys

from flask import Flask, request, Response, send_file
from werkzeug import secure_filename
from swiftclient.exceptions import ClientException

from exceptions import HttpError
from SwiftConnect import SwiftConnect
import appConfig


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(module)s - %(levelname)s ##\t  %(message)s")
log = logging.getLogger()

# Initialize the Flask application
# app = Flask(__name__)
app = Flask(__name__, static_folder="angular")

# Instantiating SwiftClient
swift = SwiftConnect(appConfig.swift_type, appConfig.swift_url, appConfig.swift_user, appConfig.swift_pw)



##############################################################################
# decorators
##############################################################################

def log_requests(f):
    @wraps(f)
    def logging_wrapper(*args, **kwargs):
        log.debug("request: {} {} handled by function: {}".format(request.method, request.url, f.__name__))
        return f(*args, **kwargs)
    return logging_wrapper



##############################################################################
# error handler
##############################################################################

@app.errorhandler(HttpError)
def handle_invalid_usage(error):
    return error.to_string(), error.status_code



##############################################################################
# views
##############################################################################

"""
    This route will show a form to perform an AJAX request
    jQuery is loaded to execute the request and update the
    value of the operation
"""
@app.route("/")
@app.route("/<path:path>")
def index(path=""):
    if path[:5] != "swift":
        # return render_template('index.html')
        return send_file("angular/index.html")

##############################################################################

"""
    returns the json schema for object classes
"""
@app.route("/swift/objectclassschema", methods=["GET"])
@log_requests
def get_objectclass_schema():
    ## TODO: initial insert
    acc_metadata = swift.get_account_metadata()
    return acc_metadata.get("x-objectclass-schema")

##############################################################################

"""
    returns the list of all object classes
"""
@app.route("/swift/objectclasses", methods=["GET"])
@log_requests
def get_objectclasses():
    acc_metadata = swift.get_account_metadata()
    metadata_keys = acc_metadata.keys()
    class_names = [key[14:] for key in metadata_keys if key.startswith("x-objectclass")]
    
    resp = {}
    resp["metadata"] = {"classCount": len(class_names)}
    resp["classes"] = class_names
    return Response(json.dumps(resp, sort_keys=True), mimetype="application/json")


"""
    creates a new object class
"""
@app.route("/swift/objectclasses", methods=["POST"])
@log_requests
def create_objectclass():
    raise HttpError("function is not implemented yet", 501)
    
    class_name = ""
    acc_metadata = swift.get_account_metadata()
    if ("x-objectclass-" + class_name) in acc_metadata:
        raise HttpError("class already exists", 422)
    

##############################################################################

"""
    returns the JSON schema of the specified object class
"""
@app.route("/swift/objectclasses/<class_name>", methods=["GET"])
@log_requests
def get_objectclass(class_name):
    acc_metadata = swift.get_account_metadata()
    class_def = acc_metadata["x-objectclass-" + class_name]
    
    if not class_def:
        raise HttpError("class does not exist", 404)
    
    return Response(class_def, mimetype="application/json")


"""
    changes the specified object class
"""
@app.route("/swift/objectclasses/<class_name>", methods=["PUT"])
@log_requests
def change_objectclass(class_name):
    raise HttpError("function is not implemented yet", 501)


"""
    deletes the specified object class
"""
@app.route("/swift/objectclasses/<class_name>", methods=["DELETE"])
@log_requests
def delete_objectclass(class_name):
    raise HttpError("function is not implemented yet", 501)

##############################################################################

"""
    returns the list of containers
"""
@app.route("/swift/containers", methods=["GET"])
@log_requests
def get_containers():
    optional_params = {}

    limit = request.args.get("limit")
    if limit is not None:
        if limit.isdigit() and int(limit) > 0:
            optional_params["limit"] = int(limit)
        else:
            log.debug("invalid query parameter limit: {}, for request: {}".format(limit, request.url))
            raise HttpError("specified query parameter limit: {}, must be a positive integer".format(limit), 400)

    marker = request.args.get("marker")
    if marker is not None:
        optional_params["marker"] = marker

    prefix = request.args.get("prefix")
    if prefix is not None:
        optional_params["prefix"] = prefix

    cts = swift.get_container_list(**optional_params)

    resp = {}
    resp["metadata"] = {"containerCount": cts[0].get("x-account-container-count"),
                        "objectCount": cts[0].get("x-account-object-count")}
    resp["containers"] = cts[1]
    return Response(json.dumps(resp, sort_keys=True), mimetype="application/json")


"""
    creates a new container
"""
@app.route("/swift/containers", methods=["POST"])
@log_requests
def create_container():
    container_name = request.form["containerName"]
    
    containers = swift.get_container_list()
    if container_name in containers:
        raise HttpError("container already exists", 422)
    
    swift.create_container(container_name)
    return Response(None)

##############################################################################

"""
    deletes the specified container
"""
@app.route("/swift/containers/<container_name>", methods=["DELETE"])
@log_requests
def delete_container(container_name):
    swift.delete_container(container_name)
    return Response(None)


"""
    changes the definition of the specified container
"""
@app.route("/swift/containers/<container_name>", methods=["PUT"])
@log_requests
def change_container(container_name):
    raise HttpError("function is not implemented yet", 501)

##############################################################################

"""
    returns the list of all objects in the specified container
"""
@app.route("/swift/containers/<container_name>/objects", methods=["GET"])
@log_requests
def get_objects_in_container(container_name):
    optional_params = {}

    limit = request.args.get("limit")
    if limit is not None:
        if limit.isdigit() and int(limit) > 0:
            optional_params["limit"] = int(limit)
        else:
            log.debug("invalid query parameter limit: {}, for request: {}".format(limit, request.url))
            raise HttpError("specified query parameter limit: {}, must be a positive integer".format(limit), 400)

    marker = request.args.get("marker")
    if marker is not None:
        optional_params["marker"] = marker

    prefix = request.args.get("prefix")
    if prefix is not None:
        optional_params["prefix"] = prefix

    cts = swift.get_object_list(container_name, **optional_params)
    resp = {}
    resp["metadata"] = {"schema": "NOT IMPLEMENTED YET",
                        "objectCount": cts[0].get("x-container-object-count")}
    resp["objects"] = cts[1]
    return Response(json.dumps(resp, sort_keys=True), mimetype="application/json")


"""
    creates a new object
"""
@app.route("/swift/containers/<container_name>/objects", methods=["POST"])
@log_requests
def create_object(container_name):
    # returns werkzeug.datastructures.FileStorage i.e. file-like
    # Underlying stream is either BytesIO for small files or _TemporaryFileWrapper for large files
    file = request.files["objectName"]  
    object_name = secure_filename(file.filename)
    
    # check whether an object with the same name already exists in the same container
    all_objects = swift.get_object_list(container_name)[1]
    if object_name in [obj.get("name") for obj in all_objects]:
        raise HttpError("object with this name already exists in this container", 422)
    
    retentime = request.form["RetentionPeriod"]

    headers = {}
    if retentime:
        try:
            converted_retentime = datetime.strptime(retentime, "%Y-%m-%d")
            reten_timestamp = int(time.mktime(converted_retentime.timetuple()))
            headers["X-Object-Meta-RetentionTime"] = reten_timestamp
        except ValueError as e:
            log.debug("invalid date format for form parameter RetentionPeriod: {}, for request: {}. Expected format: yyyy-mm-dd".format(retentime))
            raise HttpError("invalid date format for form parameter RetentionPeriod: {}. Expected format: yyyy-mm-dd".format(retentime), 400)
    headers["X-Object-Meta-OwnerName"] = request.form["OwnerName"]

    swift.streaming_object_upload(object_name, container_name, file, headers)
    return Response(None)

##############################################################################

"""
    downloads the specified object
"""
@app.route("/swift/containers/<container_name>/objects/<path:object_name>", methods=["GET"])
@log_requests
def stream_object(container_name, object_name):
    obj_tupel = swift.get_object_as_generator(container_name, object_name)
    
    headers = {}
    headers["Content-Length"] = obj_tupel[0].get("content-length")

    show_inline_param = request.args.get("show_inline")
    if show_inline_param and show_inline_param == "true":
        headers["Content-Disposition"] = "inline"
    else:
        headers["Content-Disposition"] = "attachment" 
    
    return Response(obj_tupel[1], mimetype=obj_tupel[0].get("content-type"), headers=headers)


"""
    delete the specified object
"""
@app.route("/swift/containers/<container_name>/objects/<path:object_name>", methods=["DELETE"])
@log_requests
def delete_object(container_name, object_name):
        metadata = swift.get_object_metadata(container_name, object_name)
        retentimestamp = metadata.get("x-object-meta-retentiontime")
        if (not retentimestamp or isRetentionPeriodExpired(retentimestamp)):
            swift.delete_object(container_name, object_name)
            responsemsg = dict()
            responsemsg["deletestatus"] = "done"
            return Response(json.dumps(responsemsg), mimetype="application/json")
        else:
            error_msg = "Deletion failed due to retention enforcement, file cannot be deleted till {}!".format(time.strftime("%a, %d. %B %Y", time.localtime(int(retentimestamp))))
            log.debug(error_msg)
            raise HttpError(error_msg, 412)

##############################################################################

"""
    returns the meta data of the specified object as json
"""
@app.route("/swift/containers/<container_name>/objects/<path:object_name>/details", methods=["GET"])
@log_requests
def get_object_metadata(container_name, object_name):
    metadata = swift.get_object_metadata(container_name, object_name)
    
    retention_timestamp = metadata.get("x-object-meta-retentiontime")
    if retention_timestamp:
        # convert time stamp to human readable format
        metadata["x-object-meta-retentiontime"] = time.strftime("%a, %d. %B %Y", time.localtime(int(retention_timestamp)))
    
    as_json = json.dumps(metadata, sort_keys=True)
    return Response(as_json, mimetype="application/json")


"""
    changes the meta data of the specified object
"""
@app.route("/swift/containers/<container_name>/objects/<path:object_name>/details", methods=["PUT"])
@log_requests
def change_object_metadata(container_name, object_name):
    raise HttpError("funcion not implemented yet")

##############################################################################

# TODO scheduler
# TODO what should we do about the files which have no retention date
@app.route("/swift/containers/<containerName>/CheckOldFiles/", methods=["GET"])
@log_requests
def check_old_files(containerName, doDelete=False):
    log.debug(containerName)
    files = swift.get_object_list(containerName)
    oldFiles = {}
    filenames = list()
    for file in files:
        log.debug("{0}\t{1}\t{2}".format(file["name"], file["bytes"], file["last_modified"]))
        fileMetaDict = swift.get_object_metadata(containerName, file["name"])
        log.debug(fileMetaDict)
        log.debug(file["name"])
        log.debug(fileMetaDict["x-object-meta-retentiontime"])
        retentimestamp = fileMetaDict["x-object-meta-retentiontime"]

        if (isRetentionPeriodExpired(retentimestamp)):
            filenames.append(file["name"])


    log.debug(filenames)
    responseObj = {"list": filenames}
    if (doDelete):
        swift.delete_objects(containerName, filenames)
    return Response(json.dumps(responseObj), mimetype="application/json")

##############################################################################

@app.route("/swift/containers/<containerName>/DeleteOldFiles/", methods=["DELETE"])
@log_requests
def delete_old_files(containerName):
    return check_old_files(containerName, doDelete=True)



##############################################################################
# helper functions
##############################################################################

def calcTimeDifference(timestamp):
    try:
        return int(timestamp) - int(time.time())
    except ValueError:
        return False

##############################################################################

def isRetentionPeriodExpired(timestamp):
    if (calcTimeDifference(timestamp)):
        return calcTimeDifference(timestamp) <= 0
    return False

##############################################################################
# main
##############################################################################

if __name__ == "__main__":
    appPort = os.getenv("VCAP_APP_PORT", "5000")
    appHost = os.getenv("VCAP_APP_HOST", "127.0.0.1")
    app.run(
        host=appHost,
        port=int(appPort),
        debug=True
    )
