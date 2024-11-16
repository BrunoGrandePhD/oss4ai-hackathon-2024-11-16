import React from 'react';
import { Navbar, Container } from 'react-bootstrap';

const Header: React.FC = () => {
  return (
    <Navbar bg="light" expand="lg">
      <Container>
        <Navbar.Brand href="#home">Wave Map</Navbar.Brand>
      </Container>
    </Navbar>
  );
};

export default Header;