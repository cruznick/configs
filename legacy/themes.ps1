$profilePath = "C:\Users\$Env:Username\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\profiles.json"
$profile = Get-Content $ProfilePath | ConvertFrom-Json

$backupProfilePath = "$home\Documents\WindowsTerminalprofiles.json"
Write-Verbose "Backing up profile to $backupProfilePath"
$profile | ConvertTo-Json | Set-Content $backupProfilePath


# Grab all schemes from github
Function Get-WtScheme {
    <#
    .Description
    Returns color schemes from
    https://github.com/mbadolato/iTerm2-Color-Schemes/blob/master/windowsterminal
    .Parameter Url
    Url to the iTerm2 project.
    .Parameter Theme
    Specify the name of the theme that you want returned. All themes are returned by default
    .Example
    PS> Get-WtTheme
    Returns all available themes
    .Example
    PS> Get-WtTheme -Filter 'atom.json'
    Retrieves the atom.json theme.
    .Link
    https://github.com/mbadolato/iTerm2-Color-Schemes/blob/master/windowsterminal/
    .Link link to blogpost
    #>
    [cmdletbinding()]
    param(
        [string]
        $Theme = '*',

        [string]
        $Url = 'https://github.com/mbadolato/iTerm2-Color-Schemes/tree/master/windowsterminal'
    )

    $page = Invoke-WebRequest $Url -UseBasicParsing

    $links = $page.Links | Where-Object title -like "$Theme.json"

    Write-Verbose "$($links.count) links found matching $Theme"

    foreach ($link in $links) {
        # Use the raw url so raw results can be returned and output
        $base = 'https://raw.githubusercontent.com'
        $href = $link.href

        $rawUrl = $base + $href
        $rawUrl = $rawUrl.replace('/blob', '')

        Invoke-RestMethod $RawUrl
    }
}

$schemes = Get-WtScheme

Write-Verbose "We have found $($schemes.count) schemes. Great Success!!"

# This object will contain schemes from our profile and all of the schemes that we just got.
$combinedProperties = [pscustomobject]@()

# loop through the original scheme and export the properties
foreach ($scheme in ($profile.schemes)) {

    # Avoid adding duplicate schemes.
    if (-not ($combinedProperties.name -like $scheme.name)) {
        $combinedProperties += $scheme
    }
}

# Add new schemes
foreach ($scheme in $schemes) {

    if (-not ($combinedProperties.name -like $scheme.name)) {
        $combinedProperties += $scheme
    }
}

# Remove the count property from appearing in our json output.
# This only persists for the session
# See https://stackoverflow.com/questions/20848507/why-does-powershell-give-different-result-in-one-liner-than-two-liner-when-conve
Remove-TypeData System.Array -ErrorAction SilentlyContinue

$updatedSchemeObj = [pscustomobject]($combinedProperties)

$profile.schemes = $updatedSchemeObj

Write-Verbose "Updating profile.json with new schemes"
$profile |
ConvertTo-Json -Depth 8 |
Set-Content $profilePath
