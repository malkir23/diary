import copy
import bson
import pymongo
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks

from backend.services.logs import LogsService, TYPES_LOGS
from backend.services.mongo import MongoService
from backend.db.base import AssetExtraData
from backend.models.assets import AssetExtraDataModel
from backend.settings.config import settings
from backend.services.oauth2 import check_admin, check_auth

router = APIRouter()
AVAILABLE_ASSETS = settings.AVAILABLE_ASSETS
TYPE_ASSET_DATA = TYPES_LOGS.ASSET_DATA

@router.post('')
def create_or_update(payload: AssetExtraDataModel, background_tasks: BackgroundTasks,
                     auth_user: dict = Depends(check_admin),
                     user: dict = Depends(check_auth),
                     ):
    json_payload = payload.dict()
    type_asset = json_payload.get('type_asset')
    extra_data_asset = MongoService.data_to_json(AssetExtraData.find_one({'type_asset': type_asset}))
    AssetExtraData.update_one({'type_asset': type_asset}, {"$set": json_payload}, upsert=True)
    try:
        user_id = user['id']
        action = 'update' if extra_data_asset else 'create'

        background_tasks.add_task(LogsService, before_object=MongoService.convert_2_dict_mongodb(extra_data_asset) if extra_data_asset else {},
                                  after_object=json_payload, type_=TYPE_ASSET_DATA, action=action,
                                  fields=["current_share", 'position'], user_id=user_id, obj={"type_asset": type_asset})
    except Exception as e:
        print(f'Error create log for adjustment [{action}] {str(e)}')
    return {
        'result': True
    }
