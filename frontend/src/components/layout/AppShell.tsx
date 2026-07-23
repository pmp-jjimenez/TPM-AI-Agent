import { Box, Toolbar } from '@mui/material';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar, drawerWidth } from './Sidebar';
import { TopBar } from './TopBar';

export function AppShell() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <TopBar onMenuOpen={() => setMobileOpen(true)} />
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minWidth: 0,
          px: { xs: 2, sm: 3, lg: 4, xl: 5 },
          pb: { xs: 4, md: 5, xl: 6 },
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 64, md: 72 } }} />
        <Box sx={{ pt: { xs: 2.5, md: 3.5, xl: 4 } }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
