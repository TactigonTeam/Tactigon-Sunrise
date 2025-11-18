#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
# Massimiliano Bellino
# Stefano Barbareschi
#********************************************************************************

from flask import Flask, Blueprint, flash, redirect, url_for, render_template, request

from sunrise_app.modules.ros2.manager import get_ros2_interface
from sunrise_app.modules.ros2.models import Ros2Command

from sunrise_app.utils.request_utils import get_from_request

bp = Blueprint("ros2", __name__, url_prefix="/ros2", template_folder="templates")

@bp.route("/")
def index():
    app = get_ros2_interface()

    if not app:
        flash("Ros 2 interface not running", category="danger")
        return redirect(url_for("main.index"))
    
    return render_template("ros2/index.jinja", config=app.config)

@bp.route("/add", methods=["POST"])
def add():
    app = get_ros2_interface()

    if not app:
        flash("Ros 2 interface not running", category="danger")
        return redirect(url_for("main.index"))

    param_file = request.files.get("ros2_parameters", None)
    print(param_file, request.files)
    if not param_file or param_file.filename == "":
        flash("Missing parameter file!", category="danger")
        return redirect(url_for("ros2.index"))
    
    package_name = get_from_request("ros2_package")
    node_name = get_from_request("ros2_node")

    if not package_name:
        flash("Missing package name!", category="danger")
        return redirect(url_for("ros2.index"))
    
    if not node_name:
        flash("Missing node name!", category="danger")
        return redirect(url_for("ros2.index"))
    
    if app.get_package_command(package_name, node_name):
        flash(f"A configuration already exists for {package_name} {node_name}", category="danger")
        return redirect(url_for("ros2.index"))
    
    if not app.add(package_name, node_name, param_file):
        flash("An error occurred saving the configurations!", category="danger")
        return redirect(url_for("ros2.index"))
    
    app.save_config()

    flash("Node saved correclty!", category="success")
    return redirect(url_for("ros2.index"))

@bp.route("/<string:identifier>/delete")
def delete(identifier: str):
    app = get_ros2_interface()

    if not app:
        flash("Ros 2 interface not running", category="danger")
        return redirect(url_for("main.index"))

    package_name, node_name = Ros2Command.get_package_and_node_from_identifier(identifier)

    app.remove(package_name, node_name)

    flash("Node deleted correclty!", category="success")
    return redirect(url_for("ros2.index"))