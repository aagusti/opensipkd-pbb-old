from email.utils import parseaddr
from sqlalchemy import not_, or_
from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from ...models import(
    DBSession,
    )
from ...models.pemda import (
    Unit, Urusan
    )
from ...models.reklame import (
    Rekening, Reklame, Jenis
    )
from datatables import ColumnDT, DataTables
from datetime import datetime
from ...tools import create_now

SESS_ADD_FAILED = 'rekening add failed'
SESS_EDIT_FAILED = 'rekening edit failed'
   
########                    
# List #
########    
@view_config(route_name='rekening', renderer='templates/rekening/list.pt',
             permission='rekening')
def view_list(request):
    return dict(project='Pajak Reklame')
    
##########                    
# Action #
##########    
@view_config(route_name='rekening-act', renderer='json',
             permission='rekening-act')
def rekening_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('level_id'))
        columns.append(ColumnDT('is_summary'))
        columns.append(ColumnDT('defsign'))
        columns.append(ColumnDT('disabled'))
        
        query = DBSession.query(Rekening)
        rowTable = DataTables(req, Rekening, query, columns)
        return rowTable.output_result()

    elif url_dict['act']=='grid1':
        cari = 'cari' in params and params['cari'] or ''
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('level_id'))
        columns.append(ColumnDT('is_summary'))
        columns.append(ColumnDT('defsign'))
        columns.append(ColumnDT('disabled'))
        
        query = DBSession.query(Rekening
                        ).filter(or_(Rekening.nama.ilike('%%%s%%' % cari),
                                     Rekening.kode.ilike('%%%s%%' % cari),))
        rowTable = DataTables(req, Rekening, query, columns)
        return rowTable.output_result()
        
    elif url_dict['act']=='headofnama':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Rekening.id,
                               Rekening.kode, 
                               Rekening.nama
                       ).filter(Rekening.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            r.append(d)
        return r    
		
    elif url_dict['act']=='headofkode':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Rekening.id, 
                               Rekening.kode
                       ).filter(Rekening.kode.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']          = k[0]
            d['value']       = k[1]
            r.append(d)
        return r  
		
    elif url_dict['act']=='hon_pegawai':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(Rekening.id, 
                               Rekening.kode, 
                               Rekening.nama
                       ).filter(Rekening.nama.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[2]
            d['kode']    = k[1]
            r.append(d)
        return r      
    
#######    
# Add #
#######
def form_validator(form, value):
    def err_kode():
        raise colander.Invalid(form,
            'Kode %s sudah digunakan oleh ID %d' % (
                value['kode'], found.id))
    def err_nama():
        raise colander.Invalid(form,
            'Nama %s sudah digunakan oleh ID %d' % (
                value['nama'], found.id))
                
    if 'id' in form.request.matchdict:
        uid = form.request.matchdict['id']
        q = DBSession.query(Rekening).filter_by(id=uid)
        rek = q.first()
    else:
        rek = None
        
    q = DBSession.query(Rekening).filter_by(kode=value['kode'])
    found = q.first()
    if rek:
        if found and found.id != rek.id:
            err_kode()
    elif found:
        err_kode()
        
    if 'nama' in value: # optional
        found = Rekening.get_by_nama(value['nama'])
        if rek:
            if found and found.id != rek.id:
                err_nama()
        elif found:
            err_nama()

@colander.deferred
def deferred_status(node, kw):
    values = kw.get('daftar_status', [])
    return widget.SelectWidget(values=values)
    
STATUS = (
    (0, 'Active'),
    (1, 'In Active'),
    )    

class AddSchema(colander.Schema):  
    kode       = colander.SchemaNode(
                    colander.String(),
                    oid = "kode",
                    title = "Kode",)
    nama       = colander.SchemaNode(
                    colander.String(),
                    oid = "nama",
                    title = "Uraian",)
    header_id  = colander.SchemaNode(
                    colander.Integer(),
                    oid="header_id",
                    missing=colander.drop)
    header_nm  = colander.SchemaNode(
                    colander.String(),
                    oid="header_nm",
                    title="Header",
                    missing=colander.drop)
    level_id   = colander.SchemaNode(
                    colander.Integer(),
                    oid="level_id",
                    missing=colander.drop,
                    default=0,
                    title="Level")
    is_summary = colander.SchemaNode(
                    colander.Integer(),
                    oid="is_summary",
                    missing=colander.drop,
                    default=0,
                    title="Summary")
    defsign    = colander.SchemaNode(
                    colander.Integer(),
                    oid="defsign",
                    missing=colander.drop,
                    default=1,
                    title="Defsign")
    disabled   = colander.SchemaNode(
                    colander.Integer(),
                    widget=deferred_status)
                

class EditSchema(AddSchema):
    id = colander.SchemaNode(colander.String(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True))
                    

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(daftar_status=STATUS,
             )
    schema.request = request
    return Form(schema, buttons=('save','cancel'))
    
def save(values, user, row=None):
    if not row:
        row = Rekening()
        row.create_uid=user.id
        row.created = datetime.now()
    else:
        row.update_uid=user.id
        row.updated = datetime.now()
    row.from_dict(values)
    if not row.header_id or row.header_id==0 or row.header_id=='0':
        row.header_id=None
    DBSession.add(row)
    DBSession.flush()
    return row
    
# Untuk update is_summary pada header_id #      
def save_request2(row2=None):
    row2 = Rekening()
    return row2    
    
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    
    # Untuk otomatisasi level_id #    
    if 'header_id' in values and values['header_id']:
        values['level_id'] = Rekening.get_next_level(values['header_id'])
        
        row2 = DBSession.query(Rekening).filter(Rekening.id == values['header_id']).first()
        row2.is_summary=1
        save_request2(row2)
        
    row = save(values, request.user, row)
    request.session.flash('Rekening %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('rekening'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='rekening-add', renderer='templates/rekening/add.pt',
             permission='rekening-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)				
                return HTTPFound(location=request.route_url('rekening-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(Rekening).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'Rekening ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='rekening-edit', renderer='templates/rekening/edit.pt',
             permission='rekening-edit')
def view_edit(request):
    row = query_id(request).first()
    if not row:
        return id_not_found(request)
    form = get_form(request, EditSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)
            save_request(dict(controls), request, row)
        return route_list(request)
    elif SESS_EDIT_FAILED in request.session:
        return session_failed(request, SESS_EDIT_FAILED)
    values = row.to_dict()
    values['header_id'] = row and row.header_id or 0
    a = DBSession.query(Rekening).filter(Rekening.id==values['header_id']).first()
    if a:
        values['header_nm'] = a.nama
    else:
        values['header_nm'] = ''
    form.set_appstruct(values)
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='rekening-delete', renderer='templates/rekening/delete.pt',
             permission='rekening-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    uid = row.id
    
    if not row:
        return id_not_found(request)
        
    # Untuk mengecek apakah Rekening tersebut sedang dipakai oleh tabel lain. #    
    a = DBSession.query(Reklame).filter(Reklame.rekening_id==uid).first()
    if a:
        request.session.flash('Data tidak bisa dihapus, karena sudah masuk di Objek Pajak.', 'error')
        return route_list(request)
        
    b = DBSession.query(Jenis).filter(Jenis.rekening_id==uid).first()
    if b:
        request.session.flash('Data tidak bisa dihapus, karena sudah masuk di Jenis Reklame.', 'error')
        return route_list(request)
    #--------------------------------------------------------------------------------------------------------#    
    
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            msg = 'Rekening ID %d %s sudah dihapus.' % (row.id, row.nama)
            q.delete()
            DBSession.flush()
            request.session.flash(msg)
        return route_list(request)
    return dict(row=row, form=form.render())