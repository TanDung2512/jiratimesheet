from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from ..services.datahandler import DataHandler
from ..services.api import Jira
from ..services.utils import to_UTCtime
import datetime
class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    ## Remove unnecessary attributes

    task_id = fields.Many2one('project.task', 'Task', index=True)

    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    employee_id = fields.Many2one('hr.employee', "Employee")

    last_modified = fields.Datetime()

    assignee_id = fields.Many2one('hr.employee', "Employee")

    jiraKey = fields.Char()


    @api.model
    def auto_gen_new_line(self):
        taskDB = self.env['project.task'].sudo()
        task_records = taskDB.search([])

        username = self.env.user['login']
        employee_DB = self.env['hr.employee'].sudo()
        employee = employee_DB.search([('name','=',username)])

        for record in task_records :
            print("hello : ",record.project_id.id)
            self.env['account.analytic.line'].create({
                'task_id': record.id,
                'project_id': record.project_id.id,
                'employee_id': employee.id,
                'unit_amount': 0,
                'name': "test",
                'date': datetime.datetime.now() + datetime.timedelta(7),
            })

    @api.model
    def auto_sync_data(self):
        if not self.env.user["authorization"]:
            return
        dataHandler = DataHandler(self.env.user['login'])
        dataHandler.sync_data_from_jira()

    @api.multi
    def button_sync(self):
        if not self.env.user["authorization"]:
            raise UserError(_("Please authenticated"))

        dataHandler = DataHandler(self.env.user['login'])

        dataHandler.sync_data_from_jira()

        # if fail_sync_jira :
        #     raise Warning(_("problem raise when sync"))

    @api.model
    def create(self, vals):
        # put code sync to Jira here
        # if fail return pop
        if self.env.context.get("_is_sync_on_jira"):
            if not self.env.user["authorization"]:
                raise UserError(_("Please authenticated"))

            JiraAPI = Jira(self.env.user.get_authorization())
            task = self.env['project.task'].sudo().search([('id', '=', vals["task_id"])])

            time = vals["date"].strftime("%Y-%m-%dT%H:%M:%S.000%z")

            arg = {
                'task_key': task.name,
                'description': vals["name"],
                'date': time,
                'unit_amount': vals["unit_amount"]
            }

            httpResponse = JiraAPI.add_worklog(arg)

            if httpResponse:
                vals.update({'last_modified': to_UTCtime(httpResponse["updated"])})
            else:
                raise UserError(_("Falled to update"))

        return super(Timesheet, self).create(vals)

    @api.multi
    def write(self, vals):

        # # put code sync to Jira here
        # if vals.get("is_sync_on_jira"):
        #     if not self.env.user["authorization"]:
        #         raise UserError(_("Please authenticated"))
        #
        #     JiraAPI = Jira(self.env.user["authorization"])
        #     task = self.env['project.task'].sudo().search([('id', '=', vals["task_id"])])
        #
        #     time = vals["date"].strftime("%Y-%m-%dT%H:%M:%S.000%z")
        #
        #     agrs = vals
        #     agrs.update({
        #         "task_key": self.task_id.key,
        #         "worklog_id": self.id_jira
        #     })
        #
        #     httpResponse = JiraAPI.add_worklog(agrs)
        #
        #     if httpResponse:
        #         vals.update({'last_modified': to_UTCtime(httpResponse["updated"])})
        #     else:
        #         raise UserError(_("Falled to update"))
        #
        #     del vals["is_sync_on_jira"]

        return super(Timesheet,self).write(vals)
