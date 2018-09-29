import json
from flask import request, g
from sqlalchemy import and_

from seed.schema.base import BaseSchema
from seed.api.endpoints._base import RestfulBaseView
from seed.models.rolemenu import RoleMenu as RoleMenuModel
from seed.models.menu import Menu as MenuModel
from seed.utils.auth import api_require_super_admin


class RoleMenuSchema(BaseSchema):
    class Meta:
        model = RoleMenuModel

class RoleMenu(RestfulBaseView):
    """ 角色菜单设置
    """
    model_class = RoleMenuModel
    schema_class = RoleMenuSchema

    decorators = [api_require_super_admin]

    def get(self, model_id):
        """ GET
        """
        menu_datas = self._get_role_menu_datas(model_id)

        menus = self._encode_menus(menu_datas)
        return self.response_json(self.HttpErrorCode.SUCCESS, data=menus)

    def put(self, model_id=None):
        request_json = request.get_json()
        role_id, menus = model_id, request_json['menu']
        self._decode_menus(menus, role_id)
        return self.response_json(self.HttpErrorCode.SUCCESS)

    def _get_role_menu_datas(self, model_id):
        role_datas = self.session.query(RoleMenuModel)\
            .filter(RoleMenuModel.role_id==model_id, RoleMenuModel.bussiness_id==g.bussiness_id).all()
        role_permission_map = {role_datas.menu_id: role_datas.role_permission for role_data in role_datas}

        menu_datas = self.session.query(MenuModel)\
            .filter(MenuModel.bussiness_id==g.bussiness_id).all()

        menu_datas_with_permission = {}

        for menu_data in menu_datas:
            menu_data = menu_data.row2dict()
            menu_data['role_permission'] = role_permission_map.get(menu_data['id'], False)
            menu_datas_with_permission['-'.join([str(menu_data['parent_id']), str(menu_data['left_id'])])] = menu_data

        return menu_datas_with_permission

    def _encode_menus(self, menu_data):
        menus = {'id': 0}
        middle_menu = [menus]
        while middle_menu:
            current_menu = middle_menu.pop()
            parent_id, left_id = current_menu['id'], 0

            while True:
                current_key = '-'.join([str(parent_id), str(left_id)])
                if current_key not in menu_data:
                    break
                current_menu.setdefault('sub_menus', []).append(menu_data[current_key])
                middle_menu.append(menu_data[current_key])
                left_id = menu_data[current_key]['id']

        return menus.get('sub_menus', [])

    def _decode_menus(self, menus, role_id, parent_id=0, left_id=0):
        if not menus:
            return

        for menu in menus:
            # 更新或插入新的菜单
            # 获取到菜单对应的ID
            # if menu.get('role_permission', False):
            self._insert_or_update_menu(menu, role_id, menu.get('role_permission', False))
            left_id = current_id = menu['menu_id']
            self._decode_menus(menu.get('sub_menus', []), role_id=role_id, parent_id=current_id, left_id=0)

    def _insert_or_update_menu(self, menu, role_id, role_permission):
        role_menu = {
            "role_id": role_id,
            "menu_id": menu['menu_id'],
            "role_permission": role_permission
        }
        if 'id' in menu:
            role_menu['id'] = menu['id']
        schema = self.schema_class()
        datas, errors = schema.load(role_menu)
        datas.save()
        return datas.id