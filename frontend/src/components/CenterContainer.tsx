import React from 'react';
import { Container as BootstrapContainer } from 'react-bootstrap';

interface ContainerProps {
  children: React.ReactNode;
}

const CenterContainer: React.FC<ContainerProps> = ({ children }) => {
  return (
    <BootstrapContainer className="d-flex justify-content-center align-items-center">
      {children}
    </BootstrapContainer>
  );
};

export default CenterContainer;