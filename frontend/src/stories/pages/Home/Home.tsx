import DashboardIcon from '@mui/icons-material/Dashboard';
import Dashboard from '../../templates/Dashboard/Dashboard';
import Sidebar from '../../organisms/Sidebar/Sidebar';

export default function Home() {
  const nav_items = [
    ['/', 'Home', <DashboardIcon />],
    ['/login', 'Login', <DashboardIcon />],
    ['/api', 'API Test', <DashboardIcon />],
  ] as const;

  return (
    <>
      <Sidebar
        title='Period Tracker'
        nav_items={nav_items}
        active='/'
        children={<Dashboard />}
        logoutFn={() => {}}></Sidebar>
    </>
  );
}
