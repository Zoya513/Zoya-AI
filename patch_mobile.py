from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = [
    (
        'html,body{margin:0;padding:0;width:100%;height:100%}body{font-family:Arial,sans-serif;background:#fff;color:#202123}',
        'html,body{margin:0;padding:0;width:100%;height:100%;overflow:hidden}body{font-family:Arial,sans-serif;background:#fff;color:#202123;overflow:hidden}'
    ),
    (
        '@media(max-width:600px){.zora{height:100vh;height:100dvh}',
        '@media(max-width:600px){.zora{position:fixed;inset:0;width:100%;max-width:none;height:100vh;height:100dvh;margin:0}'
    ),
    (
        'isSending=false;sendButton.disabled=micButton.disabled=uploadButton.disabled=false;refreshSendState();questionInput.focus()',
        'isSending=false;sendButton.disabled=micButton.disabled=uploadButton.disabled=false;refreshSendState();try{questionInput.focus({preventScroll:true})}catch(e){questionInput.focus()}requestAnimationFrame(()=>requestAnimationFrame(()=>{chat.scrollTop=chat.scrollHeight}))'
    )
]

for old, new in replacements:
    if old not in s:
        raise SystemExit('Anchor not found: ' + old[:80])
    s = s.replace(old, new, 1)

match = re.search(r'async function handleGoogleCredential\(response\)\{.*?\}\nfunction initGoogleLogin', s, re.S)
if not match:
    raise SystemExit('Google auth handler not found')

new_handler = """async function handleGoogleCredential(response){hideAuthError();const token=String(response&&response.credential||\"\");if(!token){showAuthError('Google tidak mengirim ID Token.');return}const payload=decodeJwtPayload(token)||{};const localUser={userId:String(payload.sub||''),email:String(payload.email||''),name:String(payload.name||payload.given_name||''),picture:String(payload.picture||'')};if(!localUser.userId){showAuthError('Google User ID tidak ditemukan.');return}authToken=token;currentUser=localUser;localStorage.setItem('ZOYA_AI_GOOGLE_USER',JSON.stringify({email:localUser.email,name:localUser.name,picture:localUser.picture,userId:localUser.userId}));authReady=false;if(authScreen)authScreen.style.display='none';if(authUser)authUser.style.display='flex';if(authUserName)authUserName.textContent=localUser.name||localUser.email;if(authUserAvatar){authUserAvatar.src=localUser.picture||'';authUserAvatar.style.display=localUser.picture?'block':'none'}conversationHistory=[];lastSubstantiveAssistantText='';loadMemory();setupVoiceInput();refreshSendState();try{const result=await validateGoogleLogin(token);const user=result&&result.user||{};currentUser={userId:String(user.userId||localUser.userId),email:String(user.email||localUser.email),name:String(user.name||localUser.name),picture:String(user.picture||localUser.picture)};authReady=true;saveSession();setLoggedInUser(currentUser);refreshSendState()}catch(e){authToken='';currentUser=null;authReady=false;setLoggedInUser(null);showAuthError(e.message||'Google login gagal.')}}
function initGoogleLogin"""

s = s[:match.start()] + new_handler + s[match.end():]
p.write_text(s, encoding='utf-8')
print('PATCH_OK')
