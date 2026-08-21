import React from 'react'
import {Card, CardBody, CardTitle, CardImg, CardText} from "reactstrap"

const CardContainer = ({movie}) => {
  return (
    <Card
      className='my-2'
      style={{
        width: '18rem' ,
      }}
    >
      <CardImg src={movie.backdropPath} alt="kino_rasmi"/>
      <CardBody>
        <CardTitle tag="h2">
          {movie.title}
        </CardTitle>
        <CardText>
          {movie.overview}
        </CardText>
      </CardBody>
    </Card>
  )
}

export default CardContainer