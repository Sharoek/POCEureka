import classNames from 'classnames';
import PropTypes from 'prop-types';
import {useContext, useState} from 'react';
import {FormattedMessage} from 'react-intl';

import {ValidationErrorContext} from './ValidationErrors';

const checkHasErrors = (errors = [], fieldNames) => {
  // no field names known -> we don't know what to check, so assume no errors inside
  if (!fieldNames.length) return false;
  // check the error keys against the fieldName list
  for (const error of errors) {
    const errorKey = error[0];
    // check for exact membership
    if (fieldNames.includes(errorKey)) return true;
    // check for key prefix match for potential nested errors
    const partialMatch = fieldNames.some(name => errorKey.startsWith(`${name}.`));
    if (partialMatch) return true;
  }
  return false;
};

const Fieldset = ({
  title = '',
  children,
  extraClassName,
  collapsible,
  initialCollapsed = true,
  fieldNames = [],
  ...extra
}) => {
  const validationErrors = useContext(ValidationErrorContext);
  const hasErrorsInside = checkHasErrors(validationErrors, fieldNames);

  if (initialCollapsed && hasErrorsInside) {
    initialCollapsed = false;
  }

  const [collapsed, setCollapsed] = useState(collapsible && initialCollapsed);

  const titleNode = title ? (
    <h2>
      {title}
      {collapsible && (
        <>
          {' '}
          <a
            href="#"
            onClick={e => {
              e.preventDefault();
              setCollapsed(!collapsed);
            }}
            className="collapse-toggle"
          >
            <FormattedMessage
              description="Fieldset collapse link text"
              defaultMessage="{collapsed, select, true {(Show)} other {(Hide)}}"
              values={{collapsed}}
            />
          </a>
        </>
      )}
    </h2>
  ) : null;
  const className = classNames('module', 'aligned', extraClassName, {
    'collapse in show': collapsible,
    collapsed: collapsed,
  });

  return (
    <fieldset className={className} {...extra}>
      {titleNode}
      {!collapsed && children}
    </fieldset>
  );
};

Fieldset.propTypes = {
  title: PropTypes.node,
  children: PropTypes.node,
  collapsible: PropTypes.bool,
  initialCollapsed: PropTypes.bool,
  /**
   * List of field names to monitor for validation errors.
   *
   * If validation errors are present for any of these fields, and the fieldset is in
   * collapsed state -> ensure that the fieldset is initially opened.
   */
  fieldNames: PropTypes.arrayOf(PropTypes.string),
};

export default Fieldset;
