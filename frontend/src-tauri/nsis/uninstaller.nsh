; Business POS System - NSIS installer hooks
;
; The license file lives in %ProgramData%\Business POS System and must survive
; reinstall / update / repair. During UNINSTALL we ask the user whether they
; want to remove their license. The default button is NO, so an accidental
; click never destroys a valid license.

!macro NSIS_HOOK_PREUNINSTALL
  MessageBox MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2 \
    "Do you want to remove your license?$\r$\n$\r$\n\
     Select NO if you are simply uninstalling or reinstalling the software.$\r$\n\
     Select YES only if you are permanently moving to a different computer." \
    IDYES license_remove
  Goto license_keep
  license_remove:
    RMDir /r "$PROGRAMDATA\Business POS System"
  license_keep:
!macroend

!macro NSIS_HOOK_POSTINSTALL
!macroend
