import hashlib
import logging
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Member, Entry
# A02 FIX: from django.contrib.auth.hashers import make_password, check_password

security_log = logging.getLogger('journal.security')

def current_member(request):
    mid = request.session.get('member_id')
    return Member.objects.filter(pk=mid).first() if mid else None

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or len(password) < 8:
            messages.error(request, 'Enter a username and a password of at least 8 characters.')
        elif Member.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
        else:
            # A02 VULNERABILITY: store raw password; visible in db.sqlite3.
            Member.objects.create(username=username, password=password)
            # A02 FIX: replace the line above with:
            # Member.objects.create(username=username, password=make_password(password))
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')
    return render(request, 'journal/form.html', {'heading':'Register','fields':['username','password']})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        # A07 VULNERABILITY: unlimited login attempts, no throttling.
        # A07 FIX: uncomment the next 7 lines (requires cache in settings).
        # import hashlib as _hashlib
        # ip = request.META.get('REMOTE_ADDR', 'unknown')
        # throttle_key = 'login:' + _hashlib.sha256((ip + ':' + username).encode()).hexdigest()
        # failures = cache.get(throttle_key, 0)
        # if failures >= 5:
        #     security_log.warning('login_throttled username=%r', username)
        #     messages.error(request, 'Too many attempts; retry in 15 minutes.')
        #     return render(request, 'journal/form.html', {'heading':'Login','fields':['username','password']}, status=429)
        member = Member.objects.filter(username=username).first()
        # A02 VULNERABILITY: compare plaintext passwords.
        valid = member is not None and member.password == password
        # A02 FIX: replace the line above with:
        # valid = member is not None and check_password(password, member.password)
        if valid:
            # A07 FIX: reset throttling counter after successful login:
            # cache.delete(throttle_key)
            request.session.flush()
            request.session['member_id'] = member.pk
            return redirect('home')
        # A07 FIX: increment failed-attempt counter with a 15-minute expiry:
        # cache.set(throttle_key, failures + 1, timeout=900)
        # A09 VULNERABILITY: failures are not logged or alerted on.
        # A09 FIX: enable LOGGING in settings.py and uncomment:
        # security_log.warning('login_failed username=%r', username)
        # if cache.get(throttle_key, 0) >= 5:
        #     security_log.error('repeated_login_failures username=%r', username)
        messages.error(request, 'Invalid credentials.')
    return render(request, 'journal/form.html', {'heading':'Login','fields':['username','password']})

@require_POST
def logout_view(request):
    request.session.flush()
    return redirect('login')

def home(request):
    member = current_member(request)
    if member is None: return redirect('login')
    return render(request, 'journal/home.html', {'member':member,'entries':Entry.objects.filter(owner=member).order_by('-created_at')})

def new_entry(request):
    member = current_member(request)
    if member is None: return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title','').strip()[:150]
        body = request.POST.get('body','')
        if title:
            Entry.objects.create(owner=member,title=title,body=body)
            return redirect('home')
        messages.error(request,'Title required.')
    return render(request,'journal/entry_form.html',{'heading':'New entry'})

def edit_entry(request,entry_id):
    member = current_member(request)
    if member is None: return redirect('login')
    # A01 VULNERABILITY: any logged-in member can edit any entry by changing its ID.
    entry = get_object_or_404(Entry,pk=entry_id)
    # A01 FIX: replace the line above with:
    # entry = get_object_or_404(Entry,pk=entry_id,owner=member)
    if request.method == 'POST':
        entry.title = request.POST.get('title','').strip()[:150]
        entry.body = request.POST.get('body','')
        if entry.title:
            entry.save()
            return redirect('home')
        messages.error(request,'Title required.')
    return render(request,'journal/entry_form.html',{'heading':'Edit entry','entry':entry})

@require_POST
def delete_entry(request,entry_id):
    member = current_member(request)
    if member is None: return redirect('login')
    # A01 VULNERABILITY: same ownership bypass for deletion.
    entry = get_object_or_404(Entry,pk=entry_id)
    # A01 FIX: replace the line above with:
    # entry = get_object_or_404(Entry,pk=entry_id,owner=member)
    entry.delete()
    return redirect('home')

def search(request):
    member = current_member(request)
    if member is None: return redirect('login')
    term = request.GET.get('q','')
    # A03 VULNERABILITY: untrusted term becomes SQL syntax; UNION injection is possible.
    sql = f"SELECT id, title, body FROM journal_entry WHERE owner_id = {member.pk} AND title LIKE '%{term}%'"
    # A03 FIX: replace the sql line above and cursor.execute(sql) below with:
    # sql = 'SELECT id, title, body FROM journal_entry WHERE owner_id = %s AND title LIKE %s'
    # cursor.execute(sql, [member.pk, '%' + term + '%'])
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
    return render(request,'journal/search.html',{'term':term,'rows':rows})
