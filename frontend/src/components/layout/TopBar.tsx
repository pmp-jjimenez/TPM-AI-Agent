import AccountCircleOutlinedIcon from '@mui/icons-material/AccountCircleOutlined';
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined';
import MenuRoundedIcon from '@mui/icons-material/MenuRounded';
import NotificationsNoneOutlinedIcon from '@mui/icons-material/NotificationsNoneOutlined';
import SearchOutlinedIcon from '@mui/icons-material/SearchOutlined';
import { AppBar, Box, Divider, IconButton, Stack, Toolbar, Tooltip, Typography } from '@mui/material';
import { useLocation } from 'react-router-dom';
import { drawerWidth } from './Sidebar';

interface TopBarProps {
  onMenuOpen: () => void;
}

function pageTitle(pathname: string) {
  if (pathname === '/programs') return 'Programs';
  if (pathname.startsWith('/programs/')) return 'Program Workspace';
  return 'Workspace';
}

const futureActions = [
  { label: 'Search', icon: <SearchOutlinedIcon /> },
  { label: 'Notifications', icon: <NotificationsNoneOutlinedIcon /> },
  { label: 'AI Assistant', icon: <AutoAwesomeOutlinedIcon /> },
  { label: 'User menu', icon: <AccountCircleOutlinedIcon /> },
];

export function TopBar({ onMenuOpen }: TopBarProps) {
  const location = useLocation();

  return (
    <AppBar
      position="fixed"
      color="inherit"
      sx={{
        width: { md: `calc(100% - ${drawerWidth}px)` },
        ml: { md: `${drawerWidth}px` },
        borderBottom: 1,
        borderColor: 'divider',
        boxShadow: 'none',
        zIndex: (theme) => theme.zIndex.drawer - 1,
      }}
    >
      <Toolbar sx={{ minHeight: { xs: 64, md: 72 }, px: { xs: 2, sm: 3, lg: 4 } }}>
        <IconButton aria-label="Open navigation" edge="start" onClick={onMenuOpen} sx={{ mr: 1.5, display: { md: 'none' } }}>
          <MenuRoundedIcon />
        </IconButton>
        <Stack direction="row" alignItems="center" spacing={1.5} sx={{ minWidth: 0 }}>
          <Typography sx={{ fontSize: '0.875rem', fontWeight: 700, whiteSpace: 'nowrap' }}>
            TPM Operating System
          </Typography>
          <Divider orientation="vertical" flexItem sx={{ display: { xs: 'none', sm: 'block' } }} />
          <Typography component="div" sx={{ display: { xs: 'none', sm: 'block' }, fontSize: '0.95rem', fontWeight: 650, color: 'text.primary', whiteSpace: 'nowrap' }}>
            {pageTitle(location.pathname)}
          </Typography>
        </Stack>
        <Box sx={{ flexGrow: 1 }} />
        <Stack direction="row" spacing={0.25} aria-label="Future workspace actions">
          {futureActions.map((action) => (
            <Tooltip key={action.label} title={`${action.label} — coming soon`}>
              <span>
                <IconButton disabled aria-label={`${action.label} coming soon`} size="small" sx={{ display: action.label === 'AI Assistant' ? { xs: 'none', sm: 'inline-flex' } : 'inline-flex' }}>
                  {action.icon}
                </IconButton>
              </span>
            </Tooltip>
          ))}
        </Stack>
      </Toolbar>
    </AppBar>
  );
}
