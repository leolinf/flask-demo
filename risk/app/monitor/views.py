# -*- coding: utf-8 -*-

import datetime
from io import BytesIO

from flask import g, send_file
from flask_restful import Resource
import xlrd
import xlsxwriter
from sqlalchemy.orm import scoped_session

from app.models.mongos import MonitorSearch, ImportSearch, Uploading
from app.models.sqlas import Monitor
from app.constants import Code, MonitorStatus
from app.core.functions import make_response, datetime2timestamp
from app.core.managers import ExcelManager

from .parsers import (
    monitor_add_parser, monitor_single_parser, import_search_parser,
    monitor_multi_parser, monitor_search
)

from .utils import (
    get_single_monitor
)
from app.bases import BaseResource
from app.core.utils import modify_phone, get_args
from app.databases import session_scope, Session
from app.config import Config
from .managers import MonitorManager
from app.credit.utils import check_whether_self
from app.user.function import  current_user, login_required


class MonitorDetailView(Resource):

    @login_required
    def get(self):
        """贷中监控详情"""

        req = monitor_single_parser.parse_args(strict=True)

        monitor_id = req['id']

        result = get_single_monitor(monitor_id)
        if result == 'not exist':
            return make_response(status=Code.MONITOR_NOT_EXIST)

        if result == 'not ready':
            return make_response(status=Code.MONITOR_NOT_READY)
        if result == 'not allowed':
            return make_response(status=Code.NOT_ALLOWED)
        return make_response(
            status=Code.SUCCESS,
            data=result,
        )


class ApiUnusualView(Resource):
    """异常趋势"""

    @login_required
    def get(self):
        req = monitor_add_parser.parse_args(strict=True)
        result = MonitorSearch.objects(monitor_id=req["id"]).first()
        if result and not check_whether_self(result):
            return make_response(status=Code.NOT_ALLOWED)
        try:
            updateTime = datetime2timestamp(result.last_update_time)
            response = {"timeLineData":result.unusual_trend,
                        "unusualNum": result.break_num,
                        "updateTime": updateTime}
        except Exception:
            return make_response(status=Code.MONITOR_NOT_EXIST)
        return make_response(data=response)


class ApiShopTrendView(Resource):
    """电商购物记录"""

    @login_required
    def get(self):

        req = monitor_add_parser.parse_args(strict=True)
        session = scoped_session(Session)
        monitor = session.query(Monitor).get(req["id"])
        monitor_data = MonitorSearch.objects(monitor_id=req["id"]).first()
        if not monitor or not monitor_data:
            session.remove()
            return make_response(status=Code.MONITOR_NOT_EXIST)
        if monitor.status == MonitorStatus.DOING:
            session.remove()
            return make_response(status=Code.MONITOR_NOT_READY)
        if not check_whether_self(monitor_data):
            session.remove()
            return make_response(status=Code.NOT_ALLOWED)
        data = {"timeLineData": monitor_data.time_line_data}
        session.remove()
        return make_response(data=data)


class UploadView(BaseResource):

    def post(self):
        """批量导入贷后监控"""

        now = datetime.datetime.utcnow()

        req = import_search_parser.parse_args(strict=True)
        search_data = req['searchData']
        content = search_data.stream.read()

        fail = 0
        success = 0

        if search_data.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':

            return make_response(Code.UNSUPPORTED_FORMAT)

        book = xlrd.open_workbook(file_contents=content)
        sheet = book.sheet_by_index(0)

        rows = sheet.nrows

        for row in range(rows):
            args = [str(i.value) for i in sheet.row(row)]
            if args and not args[0].startswith('1'):
                continue
            if len(args) < 1 or not ExcelManager.validate_monitor(*args):
                fail += 1
            else:
                success += 1

        import_search = ImportSearch(create_time=now)
        import_search.data.put(content, content_type=search_data.content_type)
        import_search.save()

        return make_response(
            data={
                'failNum': fail,
                'successNum': success,
                'id': str(import_search.id),
            },
            status=Code.SUCCESS,
        )


class MonitorTemplateView(BaseResource):

    def get(self):
        """贷中监控模板"""

        output = BytesIO()
        book = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = book.add_worksheet()
        formatter = book.add_format({'num_format': '@'})

        sheet.set_column('A:C', 20, formatter)

        sheet.write(0, 0, '手机号（必填）')
        sheet.write(0, 1, '姓名')
        sheet.write(0, 2, '身份证号')

        book.close()
        output.seek(0)

        filename = '贷后监控导入模板.xlsx'.encode().decode('unicode_escape')

        return send_file(output, attachment_filename=filename, as_attachment=True)


class MonitorMultiView(BaseResource):

    @login_required
    def get(self):
        """批量贷后监控"""

        now = datetime.datetime.now()

        req = monitor_multi_parser.parse_args(strict=True)
        session = scoped_session(Session)

        search_id = req['id']

        try:
            import_search = ImportSearch.objects.get(id=search_id)
        except:
            return make_response(status=Code.MULTI_NOT_EXIST)

        uploading = Uploading.objects(user_id=current_user.id, upload_type='B').first()

        if uploading and uploading.doing > 0:
            return make_response(status=Code.BATCH_NOT_FINISHED)

        if not uploading:
            uploading = Uploading(user_id=current_user.id, upload_type='B').save()

        content = import_search.data.read()
        content_type = import_search.data.content_type

        total = 0
        doing = 0
        duplicate = 0

        uploading.update(
            set__total=0,
            set__duplicate=0,
            set__doing=0,
            set__success=0,
        )

        if content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':

            book = xlrd.open_workbook(file_contents=content)
            sheet = book.sheet_by_index(0)
            rows = sheet.nrows

            monitor_list = []
            for row in range(rows):
                args = [str(i.value) for i in sheet.row(row)]
                if len(args) >= 1 and ExcelManager.validate_monitor(*args):
                    total += 1

                    phone = modify_phone(args[0])
                    name = get_args(args, 1, None)
                    id_num = get_args(args, 2, None)

                    monitor = MonitorSearch.objects(phone=phone, name=name, id_num=id_num, user_id=current_user.id).first()

                    if monitor:
                        duplicate += 1
                        continue
                    doing += 1

                    number = MonitorManager.generate_id(session)
                    m = Monitor(
                        id=number,
                        name=name,
                        phone=phone,
                        idcard=id_num,
                        status=MonitorStatus.DOING,
                        user_id=current_user.id,
                        company_id=current_user.company_id,
                    )
                    session.merge(m)

                    monitor = MonitorSearch(
                        monitor_id=str(number),
                        name=name,
                        phone=phone,
                        id_num=id_num,
                        status=MonitorStatus.DOING,
                        create_time=now,
                        user_id=current_user.id,
                        company_id=current_user.company_id,
                    )
                    monitor_list.append(monitor)

            if monitor_list:
                MonitorSearch.objects.insert(monitor_list)

            uploading.update(
                inc__total=total,
                inc__duplicate=duplicate,
                inc__doing=doing,
            )

            from task.tasks import monitor_single

            for monitor in monitor_list:
                monitor_single.apply_async(
                    queue=Config.MONITOR_QUEUE,
                    args=(
                        monitor.phone,
                        monitor.name,
                        monitor.id_num,
                        monitor.monitor_id,
                        True,
                    ),
                )

        else:
            return make_response(status=Code.UNSUPPORTED_FORMAT)

        return make_response(status=Code.SUCCESS)


class MonitorSearchView(Resource):

    @login_required
    def post(self):
        """添加单挑贷后监控"""

        now = datetime.datetime.now()
        req = monitor_search.parse_args()
        phone = req['phone']
        name = req['name']
        id_num = req['idNum']

        monitor = MonitorSearch.objects(phone=phone, name=name, id_num=id_num, user_id=current_user.id).first()
        if monitor:
            return make_response(status=Code.MONITOR_ALREADY_EXIST)

        company_id = current_user.company_id
        user_id = current_user.id

        session = scoped_session(Session)
        with session_scope(session) as session:
            monitor_id = MonitorManager.generate_id(session)
            m = Monitor(
                id=monitor_id,
                phone=phone,
                name=name,
                idcard=id_num,
                user_id=current_user.id,
                status=MonitorStatus.DOING,
                company_id=current_user.company_id,
            )
            session.add(m)

        monitor = MonitorSearch(
            monitor_id=str(monitor_id),
            name=name,
            phone=phone,
            id_num=id_num,
            status=MonitorStatus.DOING,
            create_time=now,
            user_id=user_id,
            company_id=company_id,
        ).save()

        from task.tasks import monitor_single

        monitor_single.apply_async(
            queue=Config.MONITOR_QUEUE,
            args=(
                phone,
                name,
                id_num,
                str(monitor_id),
            ),
        )

        return make_response({
            'id': str(monitor_id),
        })
