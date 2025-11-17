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
#********************************************************************************/

import json
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from flask import Blueprint, render_template, flash, redirect, url_for

from sunrise_app.modules.socketio import get_socket_app

from sunrise_app.modules.mqtt.models import MQTTConfig

from sunrise_app.modules.shapes.extension import ShapeConfig, Program
from sunrise_app.modules.shapes.manager import get_shapes_app

from sunrise_app.modules.zion.manager import get_zion_interface

from sunrise_app.config import app_config
from sunrise_app.utils.request_utils import get_from_request, check_empty_inputs

from sunrise_app.modules.ros2.extension import Ros2Interface
from sunrise_app.modules.ros2.models import Ros2Subscription, Ros2Publisher, Ros2ShapeConfig
from sunrise_app.modules.ros2.manager import get_ros2_interface

from sunrise_app.modules.mqtt.models import MQTTSubscription


bp = Blueprint("shapes", __name__, url_prefix="/shapes", template_folder="templates", static_folder="static")

@bp.route("/")
@bp.route("/<string:program_id>")
def index(program_id: Optional[str] = None):
    _shapes = get_shapes_app()

    if not _shapes:
        flash("Shapes app not found", category="danger")
        return redirect(url_for("main.index"))

    current_config: Optional[ShapeConfig] = None

    if program_id:
        program = _shapes.find_shape_by_id(UUID(program_id))

        if program is None:
            flash(f"Shape not found!", category="danger")
            return redirect(url_for("shapes.index"))

        current_config = program
    else:
        if any(_shapes.config):
            current_config = _shapes.config[0]

    blocks_config = _shapes.get_blocks_congfig()

    zion = get_zion_interface()

    if zion and zion.devices:
        blocks_config["zion"] = zion.get_shape_blocks()

    ros2_interface = get_ros2_interface()
    if ros2_interface:
        blocks_config["ros2"] = ros2_interface.get_blocks()
    
    state = _shapes.get_state(current_config.id) if current_config else None

    return render_template("shapes/index.jinja",
                           current_config=current_config,
                           current_running_program=_shapes.current_id,
                           is_running=_shapes.is_running,
                           state=json.dumps(state),
                           shapes_config=_shapes.config,
                           blocks_config=blocks_config,
                           )


@bp.route("/add", methods=["POST"])
def add():
    _shapes = get_shapes_app()

    if not _shapes:
        flash("Shapes app not found", category="danger")
        return redirect(url_for("main.index"))

    program_name = get_from_request('name')
    _program_description = get_from_request('description')

    if program_name is None:
        flash("Cannot add Shape, please specify a name", category="danger")
        return redirect(url_for("shapes.index"))
    
    program_name = program_name.strip()

    if program_name == "":
        flash("Cannot add Shape, please specify a name", category="danger")
        return redirect(url_for("shapes.index"))

    program = _shapes.find_shape_by_name(program_name)

    if program:
        flash(f"Name '{program_name}' already exist!", category="danger")
        return redirect(url_for("shapes.index"))
    
    mqtt_url = get_from_request("mqtt_url")
    mqtt_port = get_from_request("mqtt_port")
    mqtt_nodename = get_from_request("mqtt_nodename")
    mqtt_nodetype = get_from_request("mqtt_nodetype")
    mqtt_config = None

    if (mqtt_url and mqtt_url != "") and (mqtt_port and mqtt_port != "") and (mqtt_nodename and mqtt_nodename != "") and (mqtt_nodetype and mqtt_nodetype != ""):
        try:
            mqtt_port = int(mqtt_port)
        except:
            flash(f"Invalid MQTT port config!", category="danger")
            return redirect(url_for("shapes.index"))

        mqtt_config = MQTTConfig(
            broker_url=mqtt_url,
            broker_port=mqtt_port,
            node_name=mqtt_nodename,
            node_type=mqtt_nodetype,
        )

    new_config = ShapeConfig(
        id=uuid4(),
        name=program_name,
        description=_program_description,
        created_on=datetime.now(),
        modified_on=datetime.now(),
        mqtt_config=mqtt_config,
    )

    _shapes.add(new_config)

    flash(f"Shape created.", category="success")
    return redirect(url_for("shapes.edit", program_id=new_config.id))


@bp.route("/<string:program_id>/edit")
def edit(program_id: str):
    _shapes = get_shapes_app()

    if not _shapes:
        flash("Shapes app not found", category="danger")
        return redirect(url_for("main.index"))

    current_config = _shapes.find_shape_by_id(UUID(program_id))

    if not current_config:
        flash("Shape not found", category="danger")
        return redirect(url_for("shapes.index"))
    
    state = _shapes.get_state(current_config.id)

    blocks_config = _shapes.get_blocks_congfig()

    zion = get_zion_interface()
    if zion and zion.devices:
        blocks_config["zion"] = zion.get_shape_blocks()

    ros2_interface = get_ros2_interface()
    if ros2_interface:
        blocks_config["ros2"] = ros2_interface.get_blocks()

    return render_template("shapes/edit.jinja",
                           current_config=current_config,
                           state=json.dumps(state),
                           blocks_config=blocks_config
                           )


@bp.route("/<string:program_id>/save/config", methods=["POST"])
def save_config(program_id: str):
    _shapes = get_shapes_app()

    if not _shapes:
        flash(f"Shapes app not found!", category="danger")
        return redirect(url_for("main.index"))

    program_name = get_from_request('name')
    program_description = get_from_request('description')

    if program_name is None:
        flash("Please specify a Shape name", category="danger")
        return redirect(url_for("shapes.index", program_id=program_id))
    
    program_name = program_name.strip()

    if program_name == "":
        flash("Cannot add Shape, please specify a name", category="danger")
        return redirect(url_for("shapes.index"))

    exist_config_by_name = _shapes.find_shape_by_name_and_not_id(name=program_name, config_id=UUID(program_id))

    if exist_config_by_name:
        flash(f"Name '{program_name}' already exists!", category="danger")
        return redirect(url_for("shapes.index", program_id=program_id))
    
    config = _shapes.find_shape_by_id(UUID(program_id))

    if not config:
        flash(f"Shape not found!", category="danger")
        return redirect(url_for("shapes.index"))
  
    mqtt_url = get_from_request("mqtt_url")
    mqtt_port = get_from_request("mqtt_port")
    mqtt_nodename = get_from_request("mqtt_nodename")
    mqtt_nodetype = get_from_request("mqtt_nodetype")

    if (mqtt_url and mqtt_url != "") and (mqtt_port and mqtt_port != "") and (mqtt_nodename and mqtt_nodename != "") and (mqtt_nodetype and mqtt_nodetype != ""):
        try:
            mqtt_port = int(mqtt_port)
        except:
            flash(f"Invalid MQTT port config!", category="danger")
            return redirect(url_for("shapes.index"))

        if not config.mqtt_config:
            mqtt_config = MQTTConfig(
            broker_url=mqtt_url,
            broker_port=mqtt_port,
            node_name=mqtt_nodename,
            node_type=mqtt_nodetype,
        )
        else:
            mqtt_config = config.mqtt_config

            mqtt_config.broker_url = mqtt_url
            mqtt_config.broker_port = mqtt_port
            mqtt_config.node_name = mqtt_nodename
            mqtt_config.node_type = mqtt_nodetype
    else:
        mqtt_config = None

    config.name = program_name
    config.description = program_description
    config.modified_on = datetime.now()
    config.mqtt_config = mqtt_config

    _shapes.save_config(config=config)

    flash(f"Shape updated.", category="success")
    return redirect(url_for("shapes.index", program_id=program_id))


@bp.route("/<string:program_id>/clone/config", methods=["POST"])
def clone_config(program_id: str):
    _shapes = get_shapes_app()

    if not _shapes:
        flash(f"Shapes app not found!", category="danger")
        return redirect(url_for("main.index"))

    program_name = get_from_request('name')
    program_description = get_from_request('description')

    if program_name is None:
        flash("Please specify a Shape name", category="danger")
        return redirect(url_for("shapes.index", program_id=program_id))
    
    program_name = program_name.strip()

    if program_name == "":
        flash("Cannot add Shape, please specify a name", category="danger")
        return redirect(url_for("shapes.index"))

    original_config = _shapes.find_shape_by_id(UUID(program_id))

    if not original_config:
        flash(f"Cannot clone Shape. Shape not found.", category="danger")
        return redirect(url_for("shapes.index"))
    
    exist_config_by_name = _shapes.find_shape_by_name_and_not_id(name=program_name, config_id=UUID(program_id))

    if exist_config_by_name:
        flash(f"Name '{program_name}' already exists!", category="danger")
        return redirect(url_for("shapes.index", program_id=program_id))
    
    new_config = ShapeConfig(
        uuid4(),
        program_name,
        datetime.now(),
        datetime.now(),
        program_description,
        original_config.readonly,
        original_config.app_file,
        original_config.ros2_config,
        original_config.mqtt_config
    )

    program = _shapes.get_shape(UUID(program_id))
    is_success = _shapes.add(new_config, program)

    if not is_success:
        flash(f"Something went wrong!", category="danger")
        return redirect(url_for("shapes.index"))

    flash(f"Shape updated.", category="success")
    return redirect(url_for("shapes.edit", program_id=new_config.id))


@bp.route("/<string:program_id>/save/program", methods=["POST"])
def save_program(program_id: str):
    _shapes = get_shapes_app()

    if not _shapes:
        flash(f"Shapes app not found!", category="danger")
        return redirect(url_for("main.index"))

    code = get_from_request('generatedCode')
    state = get_from_request('state')
    subscriptions = get_from_request("subscriptions")
    ros2_publishers = get_from_request("ros2_publishers")
    ros2_subscriptions = get_from_request("ros2_subscriptions")

    # is_empty_input = check_empty_inputs(locals().items())

    # if is_empty_input or code is None or state is None:
    if code is None or state is None:
        flash(f"An error occurred while saving the Shape!", category="danger")
        return redirect(url_for("shapes.edit", program_id=program_id))

    config = _shapes.find_shape_by_id(UUID(program_id))

    if not config:
        flash(f"Shape not found!", category="danger")
        return redirect(url_for("shapes.index"))

    config.modified_on = datetime.now()
    
    if subscriptions and config.mqtt_config:
        config.mqtt_config.subscriptions = [MQTTSubscription.FromJSON(s) for s in json.loads(subscriptions)]

    print(ros2_publishers)
    print(ros2_subscriptions)

    if ros2_publishers or ros2_subscriptions:
        ros2_config = Ros2ShapeConfig(
            config.name,
            [Ros2Publisher.FromJSON(p) for p in json.loads(ros2_publishers)] if ros2_publishers else [],
            [Ros2Subscription.FromJSON(s) for s in json.loads(ros2_subscriptions)] if ros2_subscriptions else [],
        )
        config.ros2_config = ros2_config

    is_success = _shapes.update(config, Program(code=code, state=json.loads(state)))

    if not is_success:
        flash(f"Something went wrong!", category="danger")
        return redirect(url_for("shapes.edit", program_id=program_id))

    flash(f"Shape saved.", category="success")
    return redirect(url_for("shapes.index", program_id=program_id))


@bp.route("/<string:program_id>/start")
def start(program_id: str):
    _shapes = get_shapes_app()
    _socket = get_socket_app()

    if not _shapes:
        flash(f"Shapes app not found!", category="danger")
        return redirect(url_for("main.index"))

    program = _shapes.find_shape_by_id(UUID(program_id))

    if not program:
        flash(f"Shape not found!", category="danger")
        return redirect(url_for("shapes.index"))

    status = _shapes.start(program.id)

    if status is None:
        flash(f"{program.name} does not exists!", category="danger")
        return redirect(url_for("shapes.index"))
    
    status, error = status

    if status is False:
        flash(f"Failed to start {program.name}. {error}", category="danger")
        return redirect(url_for("shapes.edit", program_id=program_id))
    
    _socket.start()
          
    flash(f"{program.name} started!", category="success")
    return redirect(url_for("shapes.index", program_id=program_id))


@bp.route("/<string:program_id>/stop")
def stop(program_id: str):
    _shapes = get_shapes_app()
    _socket = get_socket_app()

    if not _shapes:
        flash(f"Shapes app not found!", category="danger")
        return redirect(url_for("main.index"))

    _shapes.stop()
    _shapes.current_id = None

    program = _shapes.find_shape_by_id(UUID(program_id))

    if not program:
        flash(f"Shape not found!", category="danger")
        return redirect(url_for("shapes.index"))

    _socket.stop()

    flash(f"{program.name} is stopped", category="success")
    return redirect(url_for("shapes.index", program_id=program_id))


@bp.route("/<string:program_id>/delete")
def delete(program_id: str):
    _shapes = get_shapes_app()

    if not _shapes:
        flash(f"Shapes app not found!", category="danger")
        return redirect(url_for("main.index"))

    config = _shapes.find_shape_by_id(UUID(program_id))

    if not config:
        flash(f"Shape not found!", category="danger")
        return redirect(url_for("shapes.index"))

    _shapes.remove(UUID(program_id))

    flash(f"Shape deleted.", category="success")
    return redirect(url_for("shapes.index"))
