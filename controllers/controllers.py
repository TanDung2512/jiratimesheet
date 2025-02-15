# -*- coding: utf-8 -*-
from odoo import http
from ..services.api import Jira
from odoo.http import request
from odoo import fields
from ..services.utils import to_UTCtime
import datetime
import pytz
from ..services.datahandler import DataHandler

from odoo.addons.web.controllers.main import Home

from ..services import crypto
class HomeExtend(Home):
    @http.route('/web/login',type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            JiraAPI = Jira()

            credentials = {
                'username' : request.params['login'],
                'password' : request.params['password']
            }

            httpResponse = JiraAPI.authentication(credentials)

            if httpResponse.status_code == 200:
                userDB = request.env['res.users'].sudo().with_context(active_test=False)

                currentUser = userDB.search([('login', '=', request.params['login'])])

                user_data_on_jira = JiraAPI.get_user(request.params['login'])

                user_timezone = user_data_on_jira["timeZone"]

                user_display_name = user_data_on_jira["displayName"]

                #If user not exist,creat one
                if not currentUser:
                    user = {
                        'login': request.params['login'],
                        'active': True,
                        'employee': True,
                        'email': request.params['login'],
                        'employee_ids': [(0, 0, {'name': user_display_name, 'work_email': request.params['login']})],
                    }
                    currentUser = request.env.ref('base.default_user').sudo().copy(user)

                #Hardcode key
                crypto_service = crypto.AESCipher()

                authorization = crypto_service.encrypt(JiraAPI.getToken())

                # Always update jira password each login time
                currentUser.sudo().write({'password': request.params['password'],
                                          'authorization': authorization,
                                          'tz': user_timezone,
                                          'name': user_display_name})

                request.env.cr.commit()

                request.env['account.analytic.line'].sudo().with_delay().sync_data(request.params['login'])

        response = super().web_login(redirect, **kw)

        return response

