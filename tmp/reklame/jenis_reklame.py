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
from ...models.reklame import (
    JenisReklame, Rekening, MasaPajak
    )
from datatables import ColumnDT, DataTables
from datetime import datetime
from ...tools import create_now,_DTnumberformat

SESS_ADD_FAILED = 'Jenis add failed'
SESS_EDIT_FAILED = 'Jenis edit failed'

########                    
# List #
########    
@view_config(route_name='reklame-jenis', renderer='templates/jenis/list.pt',
             permission='reklame-jenis')
def view_list(request):
    return dict(project='Pajak Reklame')
    
##########                    
# Action #
##########    
@view_config(route_name='reklame-jenis-act', renderer='json',
             permission='reklame-jenis-act')
def jenis_act(request):
    ses = request.session
    req = request
    params = req.params
    url_dict = req.matchdict
    
    if url_dict['act']=='grid':
        columns = []
        columns.append(ColumnDT('id'))
        columns.append(ColumnDT('kode'))
        columns.append(ColumnDT('nama'))
        columns.append(ColumnDT('rekenings.nama'))
        columns.append(ColumnDT('tarif'))
        columns.append(ColumnDT('masa_pajaks.nama'))
        columns.append(ColumnDT('status'))
        
        query = DBSession.query(JenisReklame)
        rowTable = DataTables(req, JenisReklame, query, columns)
        return rowTable.output_result()
    
    elif url_dict['act']=='hon':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(JenisReklame.id, 
                               JenisReklame.kode, 
                               JenisReklame.nama,
                               JenisReklame.tarif,
                               JenisReklame.masa_pajak_id,
                               MasaPajak.nama.label('masa_pajak_nm'),
                               MasaPajak.pembagi,
                               MasaPajak.accres,
                               
                       ).filter(JenisReklame.nama.ilike('%%%s%%' % term) ,
                          JenisReklame.masa_pajak_id==MasaPajak.id
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']            = k[0]
            d['value']         = k[2]
            d['kode']          = k[1]
            d['nama']          = k[2]
            d['tarif']         = k[3]
            d['masa_pajak_id'] = k[4]
            d['masa_pajak_nm'] = k[5]
            d['pembagi']       = k[6]
            d['accres']        = k[7]
            r.append(d)
        return r   
           
    elif url_dict['act']=='hok':
        term = 'term' in params and params['term'] or '' 
        rows = DBSession.query(JenisReklame.id, 
                               JenisReklame.kode, 
                               JenisReklame.nama,
                               JenisReklame.tarif,
                       ).filter(JenisReklame.kode.ilike('%%%s%%' % term) 
                       ).all()
        r = []
        for k in rows:
            d={}
            d['id']      = k[0]
            d['value']   = k[1]
            d['kode']    = k[1]
            d['nama']    = k[2]
            d['tarif']    = k[3]
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
        q = DBSession.query(JenisReklame).filter_by(id=uid)
        nsr = q.first()
    else:
        nsr = None
        
    q = DBSession.query(JenisReklame).filter_by(kode=value['kode'])
    found = q.first()
    if nsr:
        if found and found.id != nsr.id:
            err_kode()
    elif found:
        err_kode()
        
    if 'nama' in value: # optional
        found = JenisReklame.get_by_nama(value['nama'])
        if nsr:
            if found and found.id != nsr.id:
                err_nama()
        elif found:
            err_nama()

@colander.deferred
def deferred_status(node, kw):
    values = kw.get('daftar_status', [])
    return widget.SelectWidget(values=values)
    
STATUS = (
    (1, 'Active'),
    (0, 'Inactive'),
    )    

class AddSchema(colander.Schema):
    kode            = colander.SchemaNode(
                      colander.String(),
                      oid = "kode",
                      title = "Kode",)
    nama            = colander.SchemaNode(
                      colander.String(),
                      oid = "nama",
                      title = "Nama",)
    rekening_id     = colander.SchemaNode(
                      colander.Integer(),
                      oid="rekening_id",
                      missing=colander.drop)
    rekening_nm     = colander.SchemaNode(
                      colander.String(),
                      #missing=colander.drop,
                      oid="rekening_nm",
                      title="Rekening",)
    tarif     = colander.SchemaNode(
                      colander.Integer(),
                      #missing=colander.drop,
                      oid="tarif",
                      title="Tarif",)
    masa_pajak_id     = colander.SchemaNode(
                      colander.Integer(),
                      oid="masa_pajak_id",
                      missing=colander.drop)
    masa_pajak_nm     = colander.SchemaNode(
                      colander.String(),
                      #missing=colander.drop,
                      oid="masa_pajak_nm",
                      title="Masa Pajak",)
    status        = colander.SchemaNode(
                      colander.Integer(),
                      widget=deferred_status,
                      default=1)

class EditSchema(AddSchema):
    id = colander.SchemaNode(
                   colander.Integer(),
                   oid="id")
                    

def get_form(request, class_form):
    schema = class_form(validator=form_validator)
    schema = schema.bind(daftar_status=STATUS)
    schema.request = request
    return Form(schema, buttons=('save','cancel'))

def save_request1(row1=None):
    row1 = Rekening()
    return row1
    
def save(values, user, row=None):
    if not row:
        row = JenisReklame()
        row.create_uid = user.id
        row.created    = datetime.now()
    else:
        row.update_uid = user.id
        row.updated    = datetime.now()
    
    row.from_dict(values)
    DBSession.add(row)
    DBSession.flush()
    
    #Untuk update disabled pada Rekening
    #a = row.rekening_id
    #row1 = DBSession.query(Rekening).filter(Rekening.id==a).first()   
    #row1.status=1
    #save_request1(row1)
    
    return row
    
def save_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save(values, request.user, row)
    request.session.flash('Jenis reklame %s sudah disimpan.' % row.nama)
        
def route_list(request):
    return HTTPFound(location=request.route_url('reklame-jenis'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
    
@view_config(route_name='reklame-jenis-add', renderer='templates/jenis/add.pt',
             permission='reklame-jenis-add')
def view_add(request):
    form = get_form(request, AddSchema)
    if request.POST:
        if 'simpan' in request.POST:
            controls = request.POST.items()
            try:
                c = form.validate(controls)
            except ValidationFailure, e:
                return dict(form=form)				
                return HTTPFound(location=request.route_url('reklame-jenis-add'))
            save_request(dict(controls), request)
        return route_list(request)
    elif SESS_ADD_FAILED in request.session:
        return session_failed(request, SESS_ADD_FAILED)
    return dict(form=form)

########
# Edit #
########
def query_id(request):
    return DBSession.query(JenisReklame).filter_by(id=request.matchdict['id'])
    
def id_not_found(request):    
    msg = 'Jenis reklame ID %s not found.' % request.matchdict['id']
    request.session.flash(msg, 'error')
    return route_list(request)

@view_config(route_name='reklame-jenis-edit', renderer='templates/jenis/edit.pt',
             permission='reklame-jenis-edit')
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
    values['rekening_id'] = row and row.rekening_id    or 0
    values['rekening_nm'] = row and row.rekenings.nama or ''
    values['masa_pajak_id'] = row and row.masa_pajak_id    or 0
    values['masa_pajak_nm'] = row and row.masa_pajaks.nama or ''
    form.set_appstruct(values)
    return dict(form=form)

##########
# Delete #
##########    
@view_config(route_name='reklame-jenis-delete', renderer='templates/jenis/delete.pt',
             permission='reklame-jenis-delete')
def view_delete(request):
    q = query_id(request)
    row = q.first()
    uid = row.id
    
    if not row:
        return id_not_found(request)
        
    form = Form(colander.Schema(), buttons=('hapus','batal'))
    if request.POST:
        if 'hapus' in request.POST:
            try:
                msg = 'Jenis reklame ID %d %s sudah dihapus.' % (row.id, row.nama)
                q.delete()
                DBSession.flush()
                request.session.flash(msg)
            except ValidationFailure, e:
                request.session.flash('Error saat menghapus data','error')
                return dict(form=form)
            #save_request(dict(controls), request, row)
        return route_list(request)
    return dict(row=row,form=form.render())
