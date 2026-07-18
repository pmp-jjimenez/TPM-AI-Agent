import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined';
import FolderOutlinedIcon from '@mui/icons-material/FolderOutlined';
import InsertChartOutlinedIcon from '@mui/icons-material/InsertChartOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import ViewListOutlinedIcon from '@mui/icons-material/ViewListOutlined';
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from '@mui/material';
import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';

export const drawerWidth = 248;

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

interface NavigationItem {
  label: string;
  icon: ReactNode;
  path?: string;
}

const navigationItems: NavigationItem[] = [
  { label: 'Programs', path: '/programs', icon: <ViewListOutlinedIcon /> },
  { label: 'Reports', icon: <InsertChartOutlinedIcon /> },
  { label: 'Documents', icon: <FolderOutlinedIcon /> },
  { label: 'Templates', icon: <DescriptionOutlinedIcon /> },
  { label: 'Settings', icon: <SettingsOutlinedIcon /> },
];

function Navigation({ onNavigate }: { onNavigate: () => void }) {
  return (
    <Box component="nav" aria-label="Primary navigation" sx={{ px: 1.5, py: 2 }}>
      <Typography variant="overline" color="text.secondary" sx={{ px: 1.5, fontWeight: 700, letterSpacing: '0.08em' }}>
        Workspace
      </Typography>
      <List sx={{ mt: 0.75 }}>
        {navigationItems.map((item) => item.path ? (
          <ListItemButton
            key={item.label}
            component={NavLink}
            to={item.path}
            onClick={onNavigate}
            sx={{
              borderRadius: 1,
              mb: 0.5,
              '&.active': { bgcolor: '#e8eefc', color: 'primary.dark' },
              '&.active .MuiListItemIcon-root': { color: 'primary.main' },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 600, fontSize: '0.925rem' }} />
          </ListItemButton>
        ) : (
          <ListItemButton key={item.label} disabled aria-label={`${item.label} unavailable`} sx={{ borderRadius: 1, mb: 0.5 }}>
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontSize: '0.925rem' }} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}

export function Sidebar({ mobileOpen, onClose }: SidebarProps) {
  const content = (
    <>
      <Toolbar sx={{ minHeight: { xs: 64, md: 68 } }} />
      <Navigation onNavigate={onClose} />
    </>
  );

  return (
    <Box component="aside" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
      >
        {content}
      </Drawer>
      <Drawer
        variant="permanent"
        open
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', borderRightColor: 'divider' },
        }}
      >
        {content}
      </Drawer>
    </Box>
  );
}
