from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from ..services.datahandler import DataHandler
from ..services.api import Jira
import datetime
class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    ## Remove unnecessary attributes

    task_id = fields.Many2one('project.task', 'Task', index=True)

    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    employee_id = fields.Many2one('hr.employee', "Employee")

    last_modified = fields.Datetime()

    assignee_id = fields.Many2one('hr.employee', "Employee")

    is_sync_on_jira = fields.Boolean(default = False)

    jiraKey = fields.Char()

    @api.model
    def auto_gen_new_line(self):
        taskDB      = self.env['project.task'].sudo()
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
        dataHandler = DataHandler(self.env.user['login'])
        try:
          dataHandler.sync_data_from_jira()
        except Exception as e:
            print(e)

    @api.multi
    def button_sync(self):

        dataHandler = DataHandler(self.env.user['login'])

        try:
          dataHandler.sync_data_from_jira()
        except Exception as e:
            print(e)

        # if fail_sync_jira :
        #     raise Warning(_("problem raise when sync"))

    @api.model
    def create(self, vals):
        # put code sync to Jira here
        # if fail return pop

        # if vals.get("is_sync_on_jira"):
        #     if not self.env.user["authorization"]:
        #         raise UserError(_("Please authenticated"))
        #
        #     JiraAPI = Jira(self.env.user["authorization"])
        #     task = self.env['project.task'].sudo().search([('id', '=', vals["task_id"])])
        #
        #     agr = {
        #         'task_key': task.key,
        #         'description': vals["name"],
        #         'date': vals["date"],
        #         'unit_amount': vals["unit_amount"]
        #     }
        #
        #     response = JiraAPI.add_worklog(agr)
        #     if not response:
        #         raise UserError(_("Fail to update"))
        #
        #
        #     vals.update({'last_modified': response["updated"]})


        return super(Timesheet, self).create(vals)





    @api.multi
    def write(self, val):

        # put code sync to Jira here

        return super(Timesheet,self).write(val)

