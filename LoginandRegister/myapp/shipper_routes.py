from flask import Blueprint
 
shipper_bp = Blueprint("shipper", __name__)
 
@shipper_bp.route("/shipper/status", methods=["GET"])
def shipper_status():
    return {"success": True, "message": "Shipper service is running."}
 