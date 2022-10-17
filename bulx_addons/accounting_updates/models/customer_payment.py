from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError

class PaymentCustomerAccountbulx(models.Model):
    _name = "pay.customer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'date'

    safe_seq = fields.Char(string='Sequence',default='0' ,compute='cal_seq_for_treasury', store=True, copy=True)
    short_code = fields.Char(related='journal.code', store=True, copy=True)

    @api.multi
    @api.depends('state')
    def cal_seq_for_treasury(self):
        list = []
        for line in self:
            if line.state == 'journal':
                max_seq = self.env['pay.customer'].search(
                    [('short_code', '=', line.short_code), ('safe_seq', '!=', '')])
                if max_seq:
                    for rec in max_seq:
                        # if rec.safe_seq:
                            mm = rec.safe_seq.split('/')
                            second = int(mm[1])
                            list.append(second)
                        # else:
                        #     line.safe_seq = str(line.journal.code) + '/' + str(1)
                        #     break
                    counter = (max(list))
                    new = counter + 1
                    line.safe_seq = str(line.journal.code) + '/' + str(new)

                else:
                    line.safe_seq = str(line.journal.code) + '/' + str(1)

    seq = fields.Char()

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'journal':
                raise ValidationError(_('you can not delete record if it posted'))

        return super(PaymentCustomerAccountbulx, self).unlink()

    @api.model
    def create(self, vals):
        vals['seq'] = self.env['ir.sequence'].next_by_code('pay_cust_sequence')
        return super(PaymentCustomerAccountbulx, self).create(vals)

    def get_currency(self):
        return self.env['res.users'].search([('id', '=', self.env.user.id)]).company_id.currency_id.id

    payment_type = fields.Selection([('receive_money', 'Receive Money'), ('send_money', 'Send Money')],
                                    string='Payment Type', default='receive_money')
    currency_id = fields.Many2one(comodel_name="res.currency", default=get_currency)
    date = fields.Date(string='Date', default=fields.Date.today(), required=True)
    customer = fields.Many2one('res.partner', string='Receipt From/Customer')
    cus_select = fields.Char('Receipt From')
    amount = fields.Monetary('Amount', required=True)
    check_number = fields.Char('Check Number')
    with_date = fields.Date('Check Date')
    bank = fields.Char(string='Bank')
    bank_select = fields.Char('Reference')
    branch = fields.Char('Branch')
    reason = fields.Char('Description')
    journal = fields.Many2one('account.journal', string='Journal', required=True, domain="[('type','=','cash')]")
    # journal_credit_account = fields.Many2one('account.account', string='journal Account',related='journal.default_credit_account_id')
    journal_debit_account = fields.Many2one('account.account', string='journal Account',
                                            related='journal.default_debit_account_id')
    destination_account = fields.Many2one('account.account', string='Destination Account', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'reviewed'),
        ('journal', "Posted"),
    ], default='draft', track_visibility='onchange')
    move_id = fields.Many2one('account.move', string='Journal Entry',
                              readonly=True, index=True, ondelete='restrict', copy=False,
                              help="Link to the automatically generated Journal Items.")

    def create_journal_entry(self):
        move = self.env['account.move'].create({
            'journal_id': self.journal.id,
            'ref': 'Payment',
            'date': fields.datetime.today(),
        })
        if self.payment_type == 'receive_money':
            self.env['account.move.line'].with_context(check_move_validity=False).create({
                # 'line_ids': [(0, 0, {

                'account_id': self.journal_debit_account.id,
                'partner_id': self.customer.id or '',
                'move_id': move.id,
                'debit': self.amount,
                'credit': 0,
                # } )]
            })
            self.env['account.move.line'].with_context(check_move_validity=False).create({
                # 'line_ids': [(0, 0, {
                'account_id': self.destination_account.id,
                # 'account_id': self.journal.default_credit_account_id.id,
                'partner_id': self.customer.id or '',

                'debit': 0,
                'credit': self.amount,
                'move_id': move.id,
                # })]
            })
            vals = {
                'move_id': move.id,

            }
            self.write(vals)
        # elif self.payment_type == 'send_money':
        #     self.env['account.move.line'].with_context(check_move_validity=False).create({
        #         # 'line_ids': [(0, 0, {
        #
        #         'account_id': self.destination_account.id,
        #         'partner_id': self.vendor.id or '',
        #         'move_id': move.id,
        #         'debit': self.amount,
        #         'credit': 0,
        #         # } )]
        #     })
        #     self.env['account.move.line'].with_context(check_move_validity=False).create({
        #         # 'line_ids': [(0, 0, {
        #         'account_id': self.journal_credit_account.id,
        #         # 'account_id': self.journal.default_credit_account_id.id,
        #         'partner_id': self.vendor.id or '',
        #
        #         'debit': 0,
        #         'credit': self.amount,
        #         'move_id': move.id,
        #         # })]
        #     })
        #     vals = {
        #         'move_id': move.id,
        #
        #     }
        #     self.write(vals)
        self.state = 'journal'

    @api.multi
    def review(self):
        self.state = 'review'

    @api.onchange('customer')
    def bank_customer_info(self):
        if self.customer:
            self.cus_select = self.customer.name

    @api.onchange('destination_account')
    def bank_destination_account_info(self):
        if self.destination_account.user_type_id.name == 'Bank and Cash':
            self.bank = self.destination_account.name
