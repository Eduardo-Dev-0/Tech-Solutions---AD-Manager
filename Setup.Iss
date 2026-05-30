; ================================================================
;  Tech Solutions — AD Manager
;  Script de Instalação — Inno Setup 6.x
;  Autor: Eduardo Gabriel de Meneses
; ================================================================

#define AppName      "Tech Solutions AD Manager"
#define AppVersion "2.1.0"
#define AppPublisher "Tech Solutions"
#define AppExeName   "GerenciadorAD.exe"
#define AppURL       "https://github.com/seu-usuario/ad-manager-releases/releases"

; ── Raiz do projeto — caminho absoluto da sua máquina
#define AppDir "C:\ad-manager-releases\Tech-Solutions---AD-Manager"

; ================================================================
[Setup]
; ── Identificação única — gere o seu em: https://guidgenerator.com
AppId={{B7C4D2E1-9F3A-4B2C-8D1E-6F7A9B0C1D2E}

AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; ── Diretório padrão de instalação
DefaultDirName={autopf}\TechSolutions\ADManager
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; ── Permissões (exige admin)
PrivilegesRequired=admin

; ── Ícone do instalador — caminho absoluto
SetupIconFile={#AppDir}\icons\icone_ad_manager.ico
UninstallDisplayIcon={app}\icons\icone_ad_manager.ico
UninstallDisplayName={#AppName}

; ── Saída do instalador gerado
OutputDir={#AppDir}\releases
OutputBaseFilename=TechSolutions_ADManager_v{#AppVersion}_Setup

; ── Compressão máxima
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMANumBlockThreads=4

; ── Aparência
WizardStyle=modern
WizardResizable=no
WizardSizePercent=110

; ── Informações de versão
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} — Instalador
VersionInfoProductName={#AppName}
VersionInfoProductVersion={#AppVersion}
VersionInfoCopyright=Copyright (C) 2026 {#AppPublisher}

; ── Licença exibida no assistente
LicenseFile={#AppDir}\LICENSE

; ── Idioma
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage

; ── Desinstalador
CreateUninstallRegKey=yes
Uninstallable=yes

; ================================================================
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "english";             MessagesFile: "compiler:Default.isl"

; ================================================================
[Tasks]
Name: "desktopicon"; \
  Description: "Criar atalho na Área de Trabalho"; \
  GroupDescription: "Atalhos adicionais:"; \
  Flags: unchecked

; ================================================================
[Files]

; ── Executável principal (gerado pelo PyInstaller)
Source: "{#AppDir}\dist\{#AppExeName}"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

; ── Pasta de ícones completa
Source: "{#AppDir}\icons\*"; \
  DestDir: "{app}\icons"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

; ── Documentação
Source: "{#AppDir}\README.md";    DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "{#AppDir}\CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#AppDir}\LICENSE";      DestDir: "{app}"; Flags: ignoreversion

; ================================================================
[Dirs]
; Pasta de logs com permissão de escrita para o usuário
Name: "{app}\logs"; Permissions: users-modify

; ================================================================
[Icons]

; ── Menu Iniciar
Name: "{group}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  IconFilename: "{app}\icons\icone_ad_manager.ico"; \
  Comment: "Gerenciador de usuários do Active Directory"

Name: "{group}\Desinstalar {#AppName}"; \
  Filename: "{uninstallexe}"; \
  IconFilename: "{app}\icons\icone_ad_manager.ico"

; ── Área de Trabalho (opcional)
Name: "{autodesktop}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  IconFilename: "{app}\icons\icone_ad_manager.ico"; \
  Tasks: desktopicon; \
  Comment: "Gerenciador de usuários do Active Directory"

; ================================================================
[Run]
; Oferecer iniciar o app ao finalizar a instalação
Filename: "{app}\{#AppExeName}"; \
  Description: "Iniciar {#AppName} agora"; \
  Flags: nowait postinstall skipifsilent shellexec; \
  Check: not WizardSilent

; ================================================================
[UninstallDelete]
; Remove a pasta de logs ao desinstalar
Type: filesandordirs; Name: "{app}\logs"

; ================================================================
[Registry]
Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: string; ValueName: "DisplayName"; \
  ValueData: "{#AppName}"; Flags: uninsdeletekey

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: string; ValueName: "DisplayVersion"; \
  ValueData: "{#AppVersion}"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: string; ValueName: "Publisher"; \
  ValueData: "{#AppPublisher}"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: string; ValueName: "URLInfoAbout"; \
  ValueData: "{#AppURL}"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: string; ValueName: "DisplayIcon"; \
  ValueData: "{app}\icons\icone_ad_manager.ico"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: dword; ValueName: "NoModify"; ValueData: "1"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}"; \
  ValueType: dword; ValueName: "NoRepair"; ValueData: "1"

; ================================================================
[Code]

// ── Verifica se o app está rodando
function AppEstaAberto(): Boolean;
begin
  Result := FindWindowByClassName('TkTopLevel') <> 0;
end;

// ── Bloqueia instalação se o app estiver aberto
function InitializeSetup(): Boolean;
begin
  if AppEstaAberto() then
  begin
    MsgBox(
      '{#AppName} está em execução.' + #13#10 + #13#10 +
      'Feche o programa antes de continuar a instalação.',
      mbError, MB_OK
    );
    Result := False;
  end
  else
    Result := True;
end;

// ── Bloqueia desinstalação se o app estiver aberto
function InitializeUninstall(): Boolean;
begin
  if AppEstaAberto() then
  begin
    MsgBox(
      '{#AppName} está em execução.' + #13#10 + #13#10 +
      'Feche o programa antes de continuar a desinstalação.',
      mbError, MB_OK
    );
    Result := False;
  end
  else
    Result := True;
end;

// ── Detecta versão anterior instalada e pergunta se quer substituir
function ChecarVersaoAnterior(): Boolean;
var
  VersaoAnterior: String;
  Resposta: Integer;
begin
  Result := True;
  if RegQueryStringValue(
    HKLM,
    'Software\Microsoft\Windows\CurrentVersion\Uninstall\{#AppName}',
    'DisplayVersion',
    VersaoAnterior
  ) then
  begin
    if VersaoAnterior <> '{#AppVersion}' then
    begin
      Resposta := MsgBox(
        'Versão anterior encontrada: v' + VersaoAnterior + #13#10 + #13#10 +
        'Deseja substituí-la pela versão {#AppVersion}?',
        mbConfirmation, MB_YESNO
      );
      if Resposta = IDNO then
        Result := False;
    end;
  end;
end;

// ── Chama verificação de versão ao avançar da tela de boas-vindas
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpWelcome then
    Result := ChecarVersaoAnterior();
end;

// ── Personaliza título e texto de boas-vindas via código
// (evita dependência de prefixo de idioma na seção [Messages])
procedure InitializeWizard();
begin
  WizardForm.Caption := '{#AppName} — Assistente de Instalação';

  WizardForm.WelcomeLabel1.Caption :=
    'Bem-vindo ao assistente de instalação do {#AppName}';

  WizardForm.WelcomeLabel2.Caption :=
    'Este assistente irá instalar o {#AppName} v{#AppVersion} '     +
    'no seu computador.' + #13#10 + #13#10 +
    'Requisitos:' + #13#10 +
    '  • Windows 10 ou superior' + #13#10 +
    '  • Conectado ao domínio Active Directory' + #13#10 +
    '  • Permissões de gerenciamento de usuários no AD' + #13#10 + #13#10 +
    'Clique em Avançar para continuar.';
end;
