import MenuRoundedIcon from '@mui/icons-material/MenuRounded';
import { AppBar, IconButton, Toolbar, Typography } from '@mui/material';

interface TopBarProps {
  onMenuOpen: () => void;
}

export function TopBar({ onMenuOpen }: TopBarProps) {
  return (
    <AppBar
      position="fixed"
      color="inherit"
      sx={{ borderBottom: 1, borderColor: 'divider', boxShadow: 'none', zIndex: (theme) => theme.zIndex.drawer + 1 }}
    >
      <Toolbar sx={{ minHeight: { xs: 64, md: 68 } }}>
        <IconButton
          aria-label="Open navigation"
          edge="start"
          onClick={onMenuOpen}
          sx={{ mr: 1.5, display: { md: 'none' } }}
        >
          <MenuRoundedIcon />
        </IconButton>
        <Typography component="div" sx={{ fontSize: '1rem', fontWeight: 700, color: '#172554', letterSpacing: '-0.01em' }}>
          TPM Operating System
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
