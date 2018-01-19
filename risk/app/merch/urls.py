# -*- encoding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from app.merch import views


merch_blue = Blueprint("merch", __name__)
merch_api = Api(merch_blue)
merch_api.add_resource(views.MerchAddEditView, '/api/modify_merchant/')
merch_api.add_resource(views.ApplySearchView, '/api/company_application/')
# merch_api.add_resource(views.GetMerchType, '/api/merchant_type/')
merch_api.add_resource(views.MerchList, '/api/merchant_list/')
merch_api.add_resource(views.MerchDetail, '/api/merchant/')
merch_api.add_resource(views.MerchCoStatus, '/api/merchant/co_status/')
merch_api.add_resource(views.CompanyUploadToken, '/api/upload_token/')
merch_api.add_resource(views.DownQrCodeView, '/api/download_code/')

merch_api.add_resource(views.CompanyInfoView, '/api/company_infor/')
#merch_api.add_resource(views.MerchUpload, '/api/upload_imgs/') # 上传图片和附件接口暂时不用
#merch_api.add_resource(views.MerchCode, '/api/download_code/')
#merch_api.add_resource(views.MerchAttachment, '/api/attachment/')
