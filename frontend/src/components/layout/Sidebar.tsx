import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import CrisisAlertOutlinedIcon from '@mui/icons-material/CrisisAlertOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined';
import FolderOpenOutlinedIcon from '@mui/icons-material/FolderOpenOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import SummarizeOutlinedIcon from '@mui/icons-material/SummarizeOutlined';
import {
  Box,
  Divider,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material';
import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';

export const drawerWidth = 264;

interface SidebarProps {
  mobileOpen: boolean;
  onClose: () => void;
}

interface NavigationItem {
  label: string;
  icon: ReactNode;
  path?: string;
}

const workspaceItems: NavigationItem[] = [
  { label: 'Dashboard', icon: <DashboardOutlinedIcon /> },
  { label: 'Programs', path: '/programs', icon: <FolderOpenOutlinedIcon /> },
  { label: 'Executive Review', icon: <AssessmentOutlinedIcon /> },
  { label: 'Major Incidents', icon: <CrisisAlertOutlinedIcon /> },
  { label: 'Operational Readiness', icon: <FactCheckOutlinedIcon /> },
  { label: 'Reports', icon: <SummarizeOutlinedIcon /> },
];

const systemItems: NavigationItem[] = [
  { label: 'Settings', icon: <SettingsOutlinedIcon /> },
];

function NavigationGroup({ label, items, onNavigate }: { label: string; items: NavigationItem[]; onNavigate: () => void }) {
  return (
    <Box sx={{ px: 1.5, py: 1.25 }}>
      <Typography variant="overline" color="text.secondary" sx={{ display: 'block', px: 1.5, mb: 0.75 }}>
        {label}
      </Typography>
      <List disablePadding>
        {items.map((item) => item.path ? (
          <ListItemButton
            key={item.label}
            component={NavLink}
            to={item.path}
            onClick={onNavigate}
            sx={{
              minHeight: 42,
              borderRadius: 1.25,
              mb: 0.25,
              color: 'text.secondary',
              '&:hover': { bgcolor: 'action.hover', color: 'text.primary' },
              '&.active': { bgcolor: 'primary.light', color: 'primary.dark' },
              '&.active .MuiListItemIcon-root': { color: 'primary.main' },
            }}
          >
            <ListItemIcon sx={{ minWidth: 36, color: 'inherit' }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 600, fontSize: '0.875rem' }} />
          </ListItemButton>
        ) : (
          <ListItemButton
            key={item.label}
            disabled
            aria-label={`${item.label} coming soon`}
            sx={{ minHeight: 42, borderRadius: 1.25, mb: 0.25, '&.Mui-disabled': { opacity: 0.55 } }}
          >
            <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} primaryTypographyProps={{ fontWeight: 500, fontSize: '0.875rem' }} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
}

function SidebarContent({ onNavigate }: { onNavigate: () => void }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100%', bgcolor: 'background.paper' }}>
      <Box sx={{ height: { xs: 64, md: 72 }, px: 3, display: 'flex', alignItems: 'center', flexShrink: 0 }}>
        <Box>
          <Typography sx={{ fontSize: '0.95rem', fontWeight: 750, letterSpacing: '-0.015em', color: 'text.primary' }}>
            TPM Operating System
          </Typography>
          <Typography variant="caption" color="text.secondary">Program workspace</Typography>
        </Box>
      </Box>
      <Divider />
      <Box component="nav" aria-label="Primary navigation" sx={{ flexGrow: 1, py: 1.25 }}>
        <NavigationGroup label="Workspace" items={workspaceItems} onNavigate={onNavigate} />
      </Box>
      <Divider sx={{ mx: 2 }} />
      <NavigationGroup label="System" items={systemItems} onNavigate={onNavigate} />
    </Box>
  );
}

export function Sidebar({ mobileOpen, onClose }: SidebarProps) {
  return (
    <Box component="aside" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
      >
        <SidebarContent onNavigate={onClose} />
      </Drawer>
      <Drawer
        variant="permanent"
        open
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', borderRightColor: 'divider' },
        }}
      >
        <SidebarContent onNavigate={onClose} />
      </Drawer>
    </Box>
  );
}
