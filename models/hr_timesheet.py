from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

import datetime
class Timesheet(models.Model):
    _inherit = 'account.analytic.line'

    ## Remove unnecessary attributes

    task_id = fields.Many2one('project.task', 'Task', index=True)

    project_id = fields.Many2one('project.project', 'Project', domain=[('allow_timesheets', '=', True)])

    employee_id = fields.Many2one('hr.employee', "Employee")

    last_modified = fields.Datetime()

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


    @api.multi
    def button_sync(self):

        fail_sync_jira = "function call to jira"
        print("hello")
        if fail_sync_jira :
            raise Warning(_("problem raise when sync"))


    @api.model
    def create(self, val):

        # put code sync to Jira here
        # if fail return pop up

        return super(Timesheet,self).create(val)


    @api.multi
    def write(self, val):

        # put code sync to Jira here

        return super(Timesheet,self).write(val)

