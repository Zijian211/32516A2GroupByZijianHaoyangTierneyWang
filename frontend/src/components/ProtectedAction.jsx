import { useAuth } from '../hooks/useAuth';

const ProtectedAction = ({ children }) => {
  const { currentUser, setShowAuthModal } = useAuth();

  if (!currentUser) {

    setShowAuthModal(true);
    return null;
  }

  return children;
};

export default ProtectedAction;